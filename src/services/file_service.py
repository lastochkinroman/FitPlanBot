"""Сервис для работы с файлами планов питания"""

import os
from pathlib import Path
from typing import List, Optional


class FileService:
    """Управление файлами для планов питания"""

    def __init__(self):
        self.base_dir = Path("files/meal_plans")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_pdf_path(self, file_path: str) -> Optional[Path]:
        """Получает полный путь к PDF файлу"""
        if not file_path:
            return None

        path = self.base_dir / file_path
        return path if path.exists() else None

    def get_image_paths(self, file_paths: List[str]) -> List[Path]:
        """Получает пути к изображениям"""
        paths = []
        for path_str in file_paths or []:
            if path_str:
                path = self.base_dir / path_str
                if path.exists():
                    paths.append(path)
        return paths


# Глобальный экземпляр
file_service = FileService()
