## **1. Project Title and Description**
### **Blender Interior Visualizer**
An AI-powered tool that generates Blender scripts for designing interior spaces based on user prompts and assets. This project combines the flexibility of Python with the power of Blender's scripting API (`bpy`) to automate interior design tasks, making it faster and error-free.

---

## **2. Features**
- Upload assets (images or textures) for custom wall, floor, and ceiling designs.
- Generate and execute Blender Python scripts from natural language prompts.
- Render high-quality interior scenes using the Blender Cycles engine.
- Streamlit-based web interface for easy interaction.
- Modular and extensible library for creating reusable Blender functions.

---

## **3. Getting Started**

### **Prerequisites**
1. Install Python 3.11 or later.
2. Install [bpy]([https://www.blender.org](https://builder.blender.org/download/bpy/)).
3. Install required Python packages (see `requirements.txt`).

### **Installation**
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/blender_interior_visualizer.git
   cd blender_interior_visualizer
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install `bpy`:
   Download the prebuilt `bpy` wheel for your platform and Python version from [Blender as a Python Module]([https://wiki.blender.org/wiki/Building_Blender/Other/BlenderAsPyModule](https://builder.blender.org/download/bpy/)).

   Example:
   ```bash
   pip install bpy-<version>.whl
   ```

### **Usage**
1. Start the Streamlit app:
   ```bash
   streamlit run main.py
   ```

2. Access the app in your browser:
   ```
   http://localhost:8501
   ```

3. Upload assets and provide a design prompt, then click "Generate Design."

---

## **4. Examples**

### **Input Prompt**
```plaintext
Design a 7x7m room with 3m ceiling. 
I want the ceiling to be covered in beige color. The first wall should be filled in 0.5x0.5m panels
with wall-textures-1000x1000 texture, the second wall should be filled in 0.5x0.25m panels with
abstract-background texture. The floor must be covered with 1x1m wood_texture panels.
```

### **Generated Scene**
- **Wall Material**: White.
- **Floor Material**: Custom wood texture.
- **Camera**: Positioned at one corner, looking at the opposite corner.

![Rendered Room](/rendered_room.png)

---

## **5. File Structure**
```
blender_interior_visualizer/
├── main.py                  # Streamlit app entry point
├── reference_script.py      # Modular library for Blender functions
├── requirements.txt         # Python dependencies
├── uploaded_assets/         # Temporary directory for uploaded assets
├── output/                  # Directory for rendered scenes
├── README.md                # Project documentation
└── .gitattributes           # Git LFS tracking for large files
```

---

## **6. Contributing**
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes and push the branch:
   ```bash
   git push origin feature-name
   ```
4. Open a pull request.

---

## **7. Acknowledgments**
- **Blender** for its powerful Python API (`bpy`).
- **Streamlit** for an intuitive web interface.
- OpenAI for inspiring natural language processing integration.
