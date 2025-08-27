import os
from pathlib import Path
import logging
from typing import List, Dict, Union

import cv2
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tensorflow import keras
import joblib
from tqdm import tqdm
from huggingface_hub import hf_hub_download
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# -------------------------
# Setup
# -------------------------
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(console.file)]
)

# --- NEW: Dedicated model storage directory ---
# Store models in a hidden directory in the user's home folder
MODEL_DIR = Path.home() / ".galamo" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True) # Ensure the directory exists

# -------------------------
# Load Models and Encoder
# -------------------------
REPO_ID = "astrodingra/galamo"
MODEL_FILES = {
    "model1": "model.keras",
    "model2": "model2.keras",
    "encoder": "encoder.pkl"
}

def download_models_if_needed():
    """Checks for models and downloads them if they are missing."""
    for key, filename in MODEL_FILES.items():
        local_path = MODEL_DIR / filename
        if not local_path.exists():
            console.log(f"[bold yellow]'{filename}' not found. Downloading...[/bold yellow]")
            try:
                hf_hub_download(
                    repo_id=REPO_ID,
                    filename=filename,
                    local_dir=MODEL_DIR,
                    local_dir_use_symlinks=False # Ensures file is copied, not linked
                )
            except Exception as e:
                console.log(f"[bold red]Error downloading '{filename}': {e}[/bold red]")
                return False
    console.log("[bold green]✔ All models are present.[/bold green]")
    return True

# --- Main model loading logic ---
if not download_models_if_needed():
    exit()

try:
    model1 = keras.models.load_model(MODEL_DIR / MODEL_FILES["model1"])
    model2 = keras.models.load_model(MODEL_DIR / MODEL_FILES["model2"])
    label_encoder = joblib.load(MODEL_DIR / MODEL_FILES["encoder"])
    console.log("[bold green]✔ Models and encoder loaded.[/bold green]")
except Exception as e:
    console.log(f"[bold red]Error loading models: {e}[/bold red]")
    exit()


# -------------------------
# Class Mappings
# -------------------------
CLASS_MAPPING_1 = {0: "Galaxy", 1: "Not a Galaxy"}
CLASS_MAPPING_2 = {
    0: ("Merger Galaxy", "Disturbed Galaxy"),
    1: ("Merger Galaxy", "Merging Galaxy"),
    2: ("Elliptical Galaxy", "Round Smooth Galaxy"),
    3: ("Elliptical Galaxy", "In-between Round Smooth Galaxy"),
    4: ("Elliptical Galaxy", "Cigar Shaped Smooth Galaxy"),
    5: ("Spiral Galaxy", "Barred Spiral Galaxy"),
    6: ("Spiral Galaxy", "Unbarred Tight Spiral Galaxy"),
    7: ("Spiral Galaxy", "Unbarred Loose Spiral Galaxy"),
    8: ("Spiral Galaxy", "Edge-on Galaxy without Bulge"),
    9: ("Spiral Galaxy", "Edge-on Galaxy with Bulge")
}

# -------------------------
# Utility Functions
# -------------------------
def preprocess_image(image_path: Union[str, Path], target_size=(128, 128)) -> np.ndarray:
    """Load and preprocess an image for prediction."""
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Cannot load image: {image_path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, target_size)
    image = image / 255.0
    return np.expand_dims(image, axis=0)

def display_prediction(image_path: Path, prediction: Dict) -> None:
    """Display a single image with a styled caption."""
    image = cv2.imread(str(image_path))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(image)
    ax.axis('off')
    confidence = prediction['Type Confidence (%)']
    caption_text = f"Type: {prediction['Type']} ({confidence:.1f}%)"
    if prediction['Type'] == "Galaxy":
        caption_text += f"\nSubclass: {prediction['Subclass']}"
    fig.text(0.5, 0.02, caption_text, wrap=True, ha="center", fontsize=12,
             bbox=dict(boxstyle="round,pad=0.5", fc="black", ec="white", lw=1, alpha=0.8))
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.show()

def display_grid(images: List[Path], predictions: List[Dict], cols: int = 3) -> None:
    """Display multiple images in a grid with styled titles."""
    rows = (len(images) + cols - 1) // cols
    plt.style.use('dark_background')
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 5.5))
    axes = axes.flatten()
    for i, (img_path, pred) in enumerate(zip(images, predictions)):
        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        axes[i].imshow(image)
        axes[i].axis('off')
        confidence = pred['Type Confidence (%)']
        title_text = f"{pred['Type']} ({confidence:.1f}%)\n"
        if pred['Type'] == "Galaxy":
            title_text += f"{pred['Subclass']}"
        axes[i].set_title(title_text, fontsize=10, pad=10)
    for i in range(len(images), len(axes)):
        axes[i].axis('off')
    plt.tight_layout()
    plt.show()

# -------------------------
# Main Predictor Class
# -------------------------
class GalaxyMorphPredictor:
    """A class to predict galaxy morphology from images."""
    def __init__(self):
        self.results: List[Dict] = []

    def __call__(self, path: Union[str, Path], show_preview: bool = True, grid_view: bool = False, recursive: bool = False):
        """
        Predicts galaxy morphology for an image or a directory of images.
        """
        path = Path(path)
        console.log(f"Attempting to find images in absolute path: [bold cyan]{path.resolve()}[/bold cyan]")
        images = self._get_images(path, recursive)
        if not images:
            console.log(f"[bold yellow]Warning: No valid images found at '{path}'.[/bold yellow]")
            return
        self.results.clear()
        console.print(Panel(f"Found {len(images)} image(s). Starting prediction...", title="[bold cyan]Prediction Initialized[/bold cyan]", border_style="cyan"))
        for img_path in tqdm(images, desc="🌠 Processing Images", unit="image"):
            try:
                prediction = self._predict(img_path)
                self.results.append(prediction)
                if show_preview and not grid_view:
                    display_prediction(img_path, prediction)
            except Exception as e:
                console.log(f"[bold red]Error processing {img_path}: {e}[/bold red]")
        if show_preview and grid_view and self.results:
            display_grid(images, self.results)
        self.print_results()

    def _get_images(self, path: Path, recursive: bool) -> List[Path]:
        """Recursively find all valid image files in a directory."""
        valid_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
        if path.is_dir():
            pattern = "**/*" if recursive else "*"
            return sorted([f for f in path.glob(pattern) if f.suffix.lower() in valid_exts])
        elif path.is_file() and path.suffix.lower() in valid_exts:
            return [path]
        return []

    def _predict(self, image_path: Path) -> Dict:
        """Run prediction on a single preprocessed image."""
        image = preprocess_image(image_path)
        pred1 = model1.predict(image, verbose=0)
        type_index = int(np.argmax(pred1))
        galaxy_type = CLASS_MAPPING_1.get(type_index, "Unknown")
        conf1 = float(np.max(pred1) * 100)
        subclass = "-"
        if galaxy_type == "Galaxy":
            pred2 = model2.predict(image, verbose=0)
            subclass_index = int(np.argmax(pred2))
            _, subclass = CLASS_MAPPING_2.get(subclass_index, ("Unknown", "Unknown"))
        return {
            "Filename": image_path.name,
            "Type": galaxy_type,
            "Type Confidence (%)": round(conf1, 2),
            "Subclass": subclass,
            "Path": str(image_path)
        }

    def print_results(self):
        """Prints the prediction results in a formatted table."""
        if not self.results: return
        table = Table(title="[bold magenta]🌌 Galaxy Morphology Prediction Results[/bold magenta]", show_header=True, header_style="bold cyan")
        table.add_column("Filename", style="dim", width=25)
        table.add_column("Type", justify="left")
        table.add_column("Confidence (%)", justify="center")
        table.add_column("Subclass", justify="left")
        for res in self.results:
            confidence_str = f"{res['Type Confidence (%)']:.2f}"
            type_style = "green" if res['Type'] == 'Galaxy' else "red"
            table.add_row(res['Filename'], f"[{type_style}]{res['Type']}[/{type_style}]", confidence_str, res['Subclass'])
        console.print(table)

    def save_csv(self, filename: Union[str, Path] = "galaxy_predictions.csv"):
        """Saves the prediction results to a CSV file."""
        if not self.results:
            console.log("[bold yellow]Warning: No results to save.[/bold yellow]")
            return
        try:
            df = pd.DataFrame(self.results)
            df.to_csv(filename, index=False)
            console.log(f"[bold green]✔ Results successfully saved to '{filename}'[/bold green]")
        except Exception as e:
            console.log(f"[bold red]Error saving CSV: {e}[/bold red]")

# -------------------------
# Exportable Instance
# -------------------------
galaxy_morph = GalaxyMorphPredictor()

# -------------------------
# Main Execution Block
# -------------------------
if __name__ == "__main__":
    image_path = "Figure_1.png"
    if not Path(image_path).exists():
         console.log(f"[bold red]Error: The file '{image_path}' was not found.[/bold red]")
         console.log("Please make sure the image file is in the same directory as the script, or provide the full path.")
    else:
        galaxy_morph(path=image_path, show_preview=True, grid_view=False)
        galaxy_morph.save_csv()
