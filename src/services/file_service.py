import os
import aiofiles
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class FileService:
    """
    Сервис для управления файлами планов питания
    """

    def __init__(self):
        # Директория для хранения файлов
        self.base_dir = Path("files")
        self.meal_plans_dir = self.base_dir / "meal_plans"
        self._ensure_directories()

    def _ensure_directories(self):
        """Создает необходимые директории"""
        self.meal_plans_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directories: {self.meal_plans_dir}")

    async def save_pdf_file(self, plan_id: str, file_data: bytes, filename: str) -> str:
        """
        Сохраняет PDF файл плана питания
        """
        file_path = self.meal_plans_dir / f"{plan_id}_pdf_{filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)

        relative_path = str(file_path.relative_to(self.base_dir))
        logger.info(f"Saved PDF file: {relative_path}")
        return relative_path

    async def save_image_file(self, plan_id: str, file_data: bytes, filename: str, index: int) -> str:
        """
        Сохраняет изображение плана питания
        """
        file_path = self.meal_plans_dir / f"{plan_id}_image_{index}_{filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)

        relative_path = str(file_path.relative_to(self.base_dir))
        logger.info(f"Saved image file: {relative_path}")
        return relative_path

    def get_pdf_path(self, pdf_file_path: str) -> Optional[Path]:
        """
        Получает полный путь к PDF файлу
        """
        if not pdf_file_path:
            return None

        full_path = self.base_dir / pdf_file_path
        if full_path.exists() and full_path.is_file():
            return full_path
        return None

    def get_image_paths(self, image_file_paths: List[str]) -> List[Path]:
        """
        Получает пути к файлам изображений
        """
        paths = []
        if not image_file_paths:
            return paths

        for path_str in image_file_paths:
            if path_str:
                full_path = self.base_dir / path_str
                if full_path.exists() and full_path.is_file():
                    paths.append(full_path)

        return paths

    async def delete_plan_files(self, plan_id: str):
        """
        Удаляет все файлы связанные с планом питания
        """
        deleted_files = []
        for file_path in self.meal_plans_dir.glob(f"{plan_id}_*"):
            if file_path.is_file():
                file_path.unlink()
                deleted_files.append(str(file_path))
                logger.info(f"Deleted file: {file_path}")

        return deleted_files

    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Получает размер файла в байтах
        """
        full_path = self.base_dir / file_path
        if full_path.exists() and full_path.is_file():
            return full_path.stat().st_size
        return None

    def validate_file_type(self, filename: str, allowed_extensions: List[str]) -> bool:
        """
        Проверяет расширение файла
        """
        if not filename:
            return False

        extension = Path(filename).suffix.lower()
        return extension in allowed_extensions


# Глобальный экземпляр сервиса
file_service = FileService()
