import argparse
import logging
import yaml
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")

def load_config(config_path="config.yaml"):
    """Load paths from standard configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_all():
    logger.info("Starting E-Commerce Analytics Pipeline...")
    config = load_config()
    
    from src.data_handler import process_file
    from src.ecommerce_model import DataLoader
    from src.data_analyzer import load_sales_data, transform_sales_data, save_analyzed_data, locate_dataset
    from src.visualization_report import load_analyzed_data, create_sales_trend_plot, create_correlation_heatmap, create_interactive_scatter
    
    raw_data_path = Path(config["paths"]["raw_data"])
    processed_data_path = Path(config["paths"]["processed_data"])
    
    # Phase 1 & 2: Process Raw File
    logger.info("Phase 1 & 2: Validating and Processing File...")
    transactions, regions = process_file(str(raw_data_path), str(processed_data_path))
    logger.info(f"Processed {len(transactions)} valid transactions.")
    
    # Phase 3: OOP Models
    logger.info("Phase 3: Loading Data Models...")
    loader = DataLoader(str(processed_data_path))
    models = loader.load_transactions()
    logger.info(f"Loaded {len(models)} robust transaction models.")
    
    # Phase 4: Data Analysis
    logger.info("Phase 4: Analyzing Data...")
    sales_csv = Path(config["paths"]["sales_data_csv"])
    analyzed_csv = Path(config["paths"]["analyzed_sales_csv"])
    
    if not sales_csv.exists():
        logger.warning(f"Sales dataset not found in {sales_csv}. Attempting locator via kagglehub...")
        sales_csv = locate_dataset()
        
    df = load_sales_data(sales_csv)
    analyzed_df, city_summary, monthly_summary = transform_sales_data(df)
    save_analyzed_data(analyzed_df, analyzed_csv)
    logger.info(f"Analysis saved to {analyzed_csv}.")
    
    # Phase 5: Visualization
    logger.info("Phase 5: Generating Visualizations...")
    reports_dir = Path(config["paths"]["reports_dir"])
    reports_dir.mkdir(exist_ok=True)
    
    vis_df = load_analyzed_data(analyzed_csv)
    create_sales_trend_plot(vis_df, reports_dir / "sales_trend.png")
    create_correlation_heatmap(vis_df, reports_dir / "correlation_matrix.png")
    create_interactive_scatter(vis_df, reports_dir / "interactive_scatter.html")
    
    logger.info("Pipeline completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="E-Commerce Analytics Pipeline")
    parser.add_argument("--run-all", action="store_true", help="Run the entire data pipeline")
    args = parser.parse_args()
    
    if args.run_all:
        run_all()
    else:
        parser.print_help()
