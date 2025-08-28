from typing import Dict
from datetime import datetime
from pathlib import Path


class FactoryEntity:
    @staticmethod
    def create_entity_file(entity_name: str, columns: Dict[str, str], output_path: str = "./") -> str:
        type_mapping = {
            str: 'String',
            int: 'Integer',
            datetime: 'DateTime',
            bool: 'Boolean',
            float: 'Float'
        }

        if 'id' not in columns:
            columns = {'id': int, **columns}

        content = (
            'from datetime import datetime\n'
            'from typing import Optional\n'
            'from sqlalchemy import String, Integer, DateTime, Boolean, Float\n'
            'from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column\n\n'
            'class Base(DeclarativeBase):\n'
            '    pass\n\n'
            f'class {entity_name.capitalize()}(Base):\n'
            f'    __tablename__ = "{entity_name.lower()}"\n\n'
        )

        for col_name, col_type in columns.items():
            is_primary = col_name == 'id'
            nullable = not is_primary
            content += (
                f"    {col_name}: Mapped[{'Optional[' if nullable else ''}"
                f"{col_type.__name__}{']' if nullable else ''}] = "
                f"mapped_column({type_mapping[col_type]}"
                f"{'' if col_type != str else '(255)'}, "
                f"{'primary_key=True, ' if is_primary else ''}"
                f"nullable={str(nullable)})\n"
            )

        file_path = Path(output_path) / f"{entity_name.lower()}.py"
        with open(file_path, 'w') as f:
            f.write(content)

        return file_path
