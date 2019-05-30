from pyoviz.BiorbdViz import BiorbdViz

# Load the model
bio = BiorbdViz(model_path="../models/Bras.bioMod", show_meshes=False)
bio.exec()  # So visualisation window doesnt shut off
