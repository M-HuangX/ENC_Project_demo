import os
import json
import shutil
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebsiteDataProcessor:
    def __init__(self, source_path, output_path):
        """
        Initialize the processor with source and output paths
        
        Args:
            source_path (str): Path to the source data directory
            output_path (str): Path where processed data will be saved
        """
        self.source_path = source_path
        self.output_path = output_path
        
        # Define subdirectories
        self.image_dir = os.path.join(source_path, 'raw_images')
        self.results_dir = os.path.join(source_path, 'raw_results')
        self.keywords_dir = os.path.join(source_path, 'keyword_identification', 'gpt-4o')
        
        # Create output directory structure
        self.output_data_dir = os.path.join(output_path, 'data')
        self.output_images_dir = os.path.join(self.output_data_dir, 'images')
        self.output_results_dir = os.path.join(self.output_data_dir, 'results')
        self.output_keywords_dir = os.path.join(self.output_data_dir, 'keywords')

    def create_directory_structure(self):
        """Create the necessary directory structure in the output path"""
        dirs_to_create = [
            self.output_data_dir,
            self.output_images_dir,
            self.output_results_dir,
            self.output_keywords_dir
        ]
        
        for dir_path in dirs_to_create:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")

    def get_models(self):
        """Get list of all available models"""
        models = [d for d in os.listdir(self.results_dir) 
                 if os.path.isdir(os.path.join(self.results_dir, d))]
        return sorted(models)

    def get_image_files(self):
        """Get list of all image files"""
        return sorted([f for f in os.listdir(self.image_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

    def get_latest_json(self, base_name, model_dir):
        """Get the latest JSON file for a given image and model"""
        json_files = [f for f in os.listdir(model_dir) if f.startswith(base_name)]
        return sorted(json_files)[-1] if json_files else None

    def process_json_content(self, json_data, is_keyword=False):
        """
        Process JSON content to keep only necessary fields
        
        Args:
            json_data (dict): The original JSON data
            is_keyword (bool): Whether this is a keyword analysis JSON
        
        Returns:
            dict: Processed JSON data
        """
        if is_keyword:
            # For keyword analysis, only keep specific fields
            return {
                "ocr_results": json_data.get("ocr_results", {}),
                "identified_keywords": json_data.get("identified_keywords", {}),
                "statistics": json_data.get("statistics", {})
            }
        else:
            # For model analysis, remove metadata
            if "metadata" in json_data:
                del json_data["metadata"]
            return json_data

    def process_files(self):
        """Process and organize all files"""
        # Get models and images
        models = self.get_models()
        images = self.get_image_files()
        
        # Save models and files lists
        with open(os.path.join(self.output_data_dir, 'models.json'), 'w') as f:
            json.dump(models, f, indent=2)
        with open(os.path.join(self.output_data_dir, 'files.json'), 'w') as f:
            json.dump(images, f, indent=2)
        
        # Copy and organize files
        for image in images:
            # Copy image
            src_image = os.path.join(self.image_dir, image)
            dst_image = os.path.join(self.output_images_dir, image)
            shutil.copy2(src_image, dst_image)
            
            # Process keywords
            base_name = os.path.splitext(image)[0]
            keyword_json = self.get_latest_json(base_name, self.keywords_dir)
            if keyword_json:
                src_keyword = os.path.join(self.keywords_dir, keyword_json)
                with open(src_keyword, 'r', encoding='utf-8') as f:
                    keyword_data = json.load(f)
                
                # Process keyword data
                processed_keyword_data = self.process_json_content(keyword_data, is_keyword=True)
                
                # Save processed keyword data
                dst_keyword = os.path.join(self.output_keywords_dir, f"{base_name}.json")
                with open(dst_keyword, 'w', encoding='utf-8') as f:
                    json.dump(processed_keyword_data, f, indent=2, ensure_ascii=False)
            
            # Process model results
            for model in models:
                model_dir = os.path.join(self.results_dir, model)
                json_file = self.get_latest_json(base_name, model_dir)
                
                if json_file:
                    # Create model directory in output
                    output_model_dir = os.path.join(self.output_results_dir, model)
                    os.makedirs(output_model_dir, exist_ok=True)
                    
                    # Read and process model results
                    src_json = os.path.join(model_dir, json_file)
                    with open(src_json, 'r', encoding='utf-8') as f:
                        model_data = json.load(f)
                    
                    # Process model data
                    processed_model_data = self.process_json_content(model_data)
                    
                    # Save processed model data
                    dst_json = os.path.join(output_model_dir, f"{base_name}.json")
                    with open(dst_json, 'w', encoding='utf-8') as f:
                        json.dump(processed_model_data, f, indent=2, ensure_ascii=False)
    def process(self):
        """Main processing function"""
        try:
            logger.info("Starting data processing...")
            self.create_directory_structure()
            self.process_files()
            logger.info("Data processing completed successfully!")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            raise

def main():
    # Configuration
    SOURCE_PATH = r"E:\ENC_analysis\\ENC_website_github\data"
    OUTPUT_PATH = r"E:\ENC_analysis\\ENC_website_github"
    
    # Create and run processor
    processor = WebsiteDataProcessor(SOURCE_PATH, OUTPUT_PATH)
    processor.process()

if __name__ == "__main__":
    main()