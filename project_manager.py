# project_manager.py

import os
import json
from pathlib import Path
from database_manager import DatabaseManager
import config
import shutil

class ProjectManager:
    MAX_RECENT_PROJECTS = 10

    def __init__(self):
        self.projects_dir = config.BASE_DIR
        self.projects_file = os.path.join(self.projects_dir, 'projects.json')
        self.projects = self.load_projects()

    def load_projects(self):
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return []
        return []

    def save_projects(self):
        try:
            with open(self.projects_file, 'w', encoding='utf-8') as file:
                json.dump(self.projects, file, indent=4)
        except Exception as e:
            print(f'Error saving projects: {e}')

    def create_project(self, project_name, directory):
        project_db_file = os.path.join(self.projects_dir, f'{project_name}.db')
        if os.path.exists(project_db_file):
            raise Exception('Projekt już istnieje.')
        db_manager = DatabaseManager(project_db_file)
        db_manager.initialize_database(directory)
        db_manager.upgrade_database()
        project = {'name': project_name, 'db_file': project_db_file}
        self.add_to_recent_projects(project)
        self.save_projects()
        return project

    def load_project(self, name):
        for project in self.projects:
            if project['name'] == name:
                if os.path.exists(project['db_file']):
                    return project
        return None

    def add_to_recent_projects(self, project_info):
        # Usunięcie istniejącego projektu o tej samej nazwie
        self.projects = [proj for proj in self.projects if proj['name'] != project_info['name']]
        # Dodanie projektu na początek listy
        self.projects.insert(0, project_info)
        # Ograniczenie listy do MAX_RECENT_PROJECTS
        self.projects = self.projects[:self.MAX_RECENT_PROJECTS]
        self.save_projects()

    def import_project(self, project_name, db_file_path):
        if not os.path.exists(db_file_path):
            raise Exception('Plik bazy danych nie istnieje.')
        if any(proj['name'] == project_name for proj in self.projects):
            raise Exception('Projekt o takiej nazwie już istnieje.')
        # Kopiowanie pliku .db do katalogu projektów
        destination_db_file = os.path.join(self.projects_dir, f'{project_name}.db')
        shutil.copy(db_file_path, destination_db_file)
        project = {'name': project_name, 'db_file': destination_db_file}
        self.add_to_recent_projects(project)
        return project

    def get_recent_projects(self):
        return self.projects
