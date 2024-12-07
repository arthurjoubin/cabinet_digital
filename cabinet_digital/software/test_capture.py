from utils import capture_website_scroll

# Test avec un site web
url = "https://www.agicap.com"  # Remplacez par l'URL que vous souhaitez tester
output_path = "cabinet_digital/software/agicap.gif"


success = capture_website_scroll(url, output_path)
if success:
    print(f"GIF créé avec succès : {output_path}")
else:
    print("Échec de la capture") 