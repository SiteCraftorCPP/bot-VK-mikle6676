"""
Скрипт для обновления PHOTO_ATTACHMENT в .env файле
"""
from pathlib import Path

env_path = Path(__file__).parent / ".env"
attachment = "photo-184746682_457239108"

if env_path.exists():
    with open(env_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    updated = False
    with open(env_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.startswith('PHOTO_ATTACHMENT='):
                f.write(f'PHOTO_ATTACHMENT={attachment}\n')
                updated = True
            else:
                f.write(line)
        
        if not updated:
            f.write(f'PHOTO_ATTACHMENT={attachment}\n')
    
    print(f"✅ .env обновлен: PHOTO_ATTACHMENT={attachment}")
else:
    print(f"❌ Файл .env не найден!")
