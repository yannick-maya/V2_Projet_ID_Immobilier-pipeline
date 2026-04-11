import sys
from pathlib import Path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
from api.main import app
import uvicorn
print(' Démarrage de l''API ID Immobilier...')
uvicorn.run(app, host='127.0.0.1', port=8000, reload=True, log_level='info')
