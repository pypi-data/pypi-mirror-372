from htmllogger import log, error, config
import time

# Configure the logger
config(max_files=5, main_filename="meu_log.html")

# Test logging
log("Mensagem azul", color="blue")
error("Algo deu errado!")

# Give some time for the logger to process messages
time.sleep(0.1)  # Small delay to ensure messages are processed
