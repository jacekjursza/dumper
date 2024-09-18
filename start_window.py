# start_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QFileDialog, QInputDialog, QMessageBox
from database_manager import DatabaseManager
from project_manager import ProjectManager
from main_window import MainWindow


class StartWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('File Merger Application - Start')
        self.setGeometry(600, 300, 400, 300)
        self.project_manager = ProjectManager()
        self.layout = QVBoxLayout(self)

        # Etykieta dla ostatnich projektów
        self.recent_projects_label = QLabel('Ostatnie Projekty:')
        self.layout.addWidget(self.recent_projects_label)

        # Lista projektów
        self.projects_list = QListWidget()
        self.layout.addWidget(self.projects_list)

        # Przycisk otwarcia projektu
        self.open_button = QPushButton('Otwórz Projekt')
        self.open_button.clicked.connect(self.open_project)
        self.layout.addWidget(self.open_button)

        # Przycisk tworzenia nowego projektu
        self.create_button = QPushButton('Utwórz Nowy Projekt')
        self.create_button.clicked.connect(self.create_new_project)
        self.layout.addWidget(self.create_button)

        # Przycisk importu projektu
        self.import_button = QPushButton('Importuj Projekt (.db)')
        self.import_button.clicked.connect(self.import_project)
        self.layout.addWidget(self.import_button)

        # Załadowanie ostatnich projektów
        self.load_recent_projects()

    def load_recent_projects(self):
        recent_projects = self.project_manager.get_recent_projects()
        self.projects_list.clear()
        for project in recent_projects:
            self.projects_list.addItem(project['name'])

    def open_project(self):
        selected_items = self.projects_list.selectedItems()
        if selected_items:
            project_name = selected_items[0].text()
            project = self.project_manager.load_project(project_name)
            if project:
                db_manager = DatabaseManager(project['db_file'])
                db_manager.upgrade_database()
                self.project_manager.add_to_recent_projects(project)
                self.open_main_window(project)
            else:
                QMessageBox.warning(self, 'Błąd',
                                    'Nie udało się załadować projektu.')
        else:
            QMessageBox.warning(self, 'Brak Wyboru',
                                'Proszę wybrać projekt do otwaria.')

    def create_new_project(self):
        project_name, ok = QInputDialog.getText(self, 'Nazwa Projektu',
                                                'Wprowadź nazwę projektu:')
        if ok and project_name:
            directory = QFileDialog.getExistingDirectory(self,
                                                         'Wybierz Katalog Projektu')
            if directory:
                try:
                    project = self.project_manager.create_project(project_name,
                                                                  directory)
                    self.open_main_window(project)
                except Exception as e:
                    QMessageBox.warning(self, 'Błąd',
                                        f'Nie udało się utworzyć projektu.\n{e}')
            else:
                QMessageBox.warning(self, 'Brak Katalogu',
                                    'Proszę wybrać katalog.')
        else:
            QMessageBox.warning(self, 'Brak Nazwy',
                                'Proszę wprowadzić nazwę projektu.')

    def import_project(self):
        # Otwarcie dialogu wyboru pliku .db
        db_file_path, _ = QFileDialog.getOpenFileName(self, 'Importuj Plik .db', '', 'SQLite DB Files (*.db);;All Files (*)')
        if db_file_path:
            # Zapytanie o nazwę projektu
            project_name, ok = QInputDialog.getText(self, 'Nazwa Projektu', 'Wprowadź nazwę projektu dla importowanego pliku:')
            if ok and project_name:
                try:
                    project = self.project_manager.import_project(project_name, db_file_path)
                    self.open_main_window(project)
                except Exception as e:
                    QMessageBox.warning(self, 'Błąd',
                                        f'Nie udało się zaimportować projektu.\n{e}')
            else:
                QMessageBox.warning(self, 'Brak Nazwy',
                                    'Proszę wprowadzić nazwę projektu.')
        else:
            QMessageBox.warning(self, 'Brak Pliku',
                                'Proszę wybrać plik .db do importu.')

    def open_main_window(self, project):
        self.main_window = MainWindow(project)
        self.main_window.show()
        self.close()
