import paramiko
import os
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    filename='sftp_transfer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def sftp_transfer():
    try:
        # Création du client SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connexion
        ssh.connect("files", 22, "files", password="files")
        
        # Création du client SFTP
        sftp = ssh.open_sftp()
        
        # Action principale
        download_files(sftp)
        
        sftp.close()
        ssh.close()
        logging.info("Transfert SFTP terminé avec succès")
        
    except Exception as e:
        logging.error(f"Erreur lors du transfert SFTP : {str(e)}")
        raise

def download_files(sftp):
    remote_files = sftp.listdir('files')
    for file in remote_files:
        try:
            remote_path = os.path.join('files', file)
            local_path = os.path.join('files', file)
            sftp.get(remote_path, local_path)
            logging.info(f"Fichier téléchargé : {file}")
            
            # Suppression désactivée
        except Exception as e:
            logging.error(f"Erreur lors du traitement du fichier {file}: {str(e)}")
            raise

def upload_files(sftp):
    local_files = os.listdir('files')
    for file in local_files:
        try:
            local_path = os.path.join('files', file)
            remote_path = os.path.join('files', file)
            sftp.put(local_path, remote_path)
            logging.info(f"Fichier envoyé : {file}")
            
            # Suppression désactivée
        except Exception as e:
            logging.error(f"Erreur lors du traitement du fichier {file}: {str(e)}")
            raise

if __name__ == '__main__':
    sftp_transfer()
