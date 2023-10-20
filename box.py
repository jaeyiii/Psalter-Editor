import sys
import os
import sqlite3
import subprocess
import platform
from pydub import AudioSegment
from PyQt5.QtGui import QIntValidator, QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QLineEdit, QListWidget, QListWidgetItem,  QFrame, QGraphicsOpacityEffect
)
import logging



class AudioCombinerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Psalter Editor")
        self.setGeometry(200, 200, 400,  250)
        self.setFixedWidth(400) #to prevent horizontal window resizing of the app
        self.setMaximumHeight(400) 

        #for the application's icon
        icon = QIcon('favicon.ico')  
        self.setWindowIcon(icon)

        # Create a frame for the gradient background
        gradient_frame = QFrame(self)
        gradient_frame.setGeometry(0, 0, 400, 400)  # Adjust the position and dimensions as needed
        
        # Load the photo
        pixmap = QPixmap('song-notes.jpg')  # the application's background photo
        background_label = QLabel(gradient_frame)
        background_label.setPixmap(pixmap)
        background_label.setGeometry(0, 0, 400, 400)

        # Apply a faded effect to the photo
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.4)  # Adjust the opacity as needed
        background_label.setGraphicsEffect(opacity_effect)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)

        # Create a horizontal layout for the Psalter Number, search bar, and search button
        search_layout = QHBoxLayout()

        # Psalter Number label
        self.stanza_label = QLabel("Psalter Number:", self)
        self.stanza_label.setFixedWidth(105) 
        search_layout.addWidget(self.stanza_label)

        # Search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText('Eg. 1. , 10. , 15.')
        self.search_bar.setMaximumWidth(100)
        search_layout.addWidget(self.search_bar)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_folder)
        search_layout.addWidget(self.search_button, alignment=Qt.AlignRight)

        # Add the search layout to the main layout
        layout.addLayout(search_layout)

        # Folder name label with a border
        self.folder_name_label = QLabel(self)
        self.folder_name_label.setStyleSheet("QLabel { padding: 4px; border: 1px solid #000; font-size: 16px; }")

        # Add the folder name label
        layout.addWidget(self.folder_name_label)

        # title of stanzas label
        additional_label = QLabel("No. of Stanzas:", self)
        additional_label_stylesheet = "QLabel { padding: 8px 0 0 0; }"
        additional_label.setStyleSheet(additional_label_stylesheet)
        layout.addWidget(additional_label, alignment=Qt.AlignLeft)

        # Create a horizontal layout for the "Stanzas" search bar and "Additional Information" label
        self.stanza_search_layout = QHBoxLayout()
        
        # add stanzas search bar
        self.stanza_search_bar = QLineEdit(self)
        self.stanza_search_bar.setPlaceholderText("Stanzas")
        self.stanza_search_bar.setMaximumWidth(100)
        self.stanza_search_bar.setValidator(QIntValidator())
        self.stanza_search_layout.addWidget(self.stanza_search_bar)
        
        #add "default" button
        self.default_button = QPushButton("Default")
        self.default_button.setMaximumWidth(60)
        self.default_button.clicked.connect(self.default)
        self.stanza_search_layout.addWidget(self.default_button)

        # Add the "response" label to the horizontal layout
        self.additional_label = QLabel("", self)
        self.additional_label.setMargin(10)
        self.additional_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.stanza_search_layout.addWidget(self.additional_label, alignment=Qt.AlignLeft)

        # add the stanza search layout to the main layout
        layout.addLayout(self.stanza_search_layout)
        
        # add Get Audio Button
        self.combine_button = QPushButton("Get Audio")
        self.combine_button.clicked.connect(self.combine_segments)
        layout.addWidget(self.combine_button, alignment=Qt.AlignLeft)
    
        # Commands triggering function initiation upon pressing the 'Enter' key
        self.search_bar.returnPressed.connect(self.search_folder)
        self.search_bar.returnPressed.connect(self.focus_second_search_bar)
        self.stanza_search_bar.returnPressed.connect(self.combine_segments)

        # initialize other layout for the playlist 
        layout2 = QVBoxLayout()

        #add label2 label in the layout2
        label2 = QLabel("Your Playlist")
        font = label2.font()
        font.setPointSize(16)
        label2.setFont(font)
        additional_label_stylesheets = "QLabel { padding: 0 0 8px 0; }"
        label2.setStyleSheet(additional_label_stylesheets)
        button2 = QPushButton("View Playlist Folder")
        button2.clicked.connect(self.open_playlist_folder)
        layout2.addWidget(label2)

        # Create a list widget to display playlist files and add it to the layout2
        self.playlist_list = QListWidget(self)
        layout2.addWidget(self.playlist_list)
        layout2.addWidget(button2, alignment=Qt.AlignRight)
        
        # add the layou2 to the main layout
        layout.addLayout(layout2)

        # Update the list widget with playlist files
        self.update_playlist_list()
        
        # Connect the 'aboutToQuit' signal to ensure the 'clear_playlist_folder' function is executed
        # when the application is about to quit to clean up any resources or files.
        app.aboutToQuit.connect(self.clear_playlist_folder)

        logging.basicConfig(filename="error.log", level=logging.ERROR) # for catching bugs and erros
        self.max_stanza = "" #A variable to store data from the .db file with a maximum stanza
        self.psalter_name = ""  #variable for psalter_name that will be used in other functions
        self.folder_path = "" #variable for folder_path that will be used in other functions


    def open_playlist_folder(self):
        """
        Opens the 'Playlist' folder in the file explorer for the user's platform.

        This function determines the user's operating system and opens the 'Playlist' folder
        using the appropriate command. It supports macOS and Windows. Custom handling may
        be needed for other platforms.

        :return: None
        """
        try:
            # Get the current directory
            current_directory = os.getcwd()
            # Create the path to the "Playlist" folder
            playlist_folder_path = os.path.join(current_directory, "Playlist")
            

            if platform.system() == "Darwin":
                # macOS
                subprocess.run(["open", playlist_folder_path])
            elif platform.system() == "Windows":
                # Windows
                print(playlist_folder_path)
                subprocess.run(["explorer", playlist_folder_path], shell=True)
            else:
                # For other platforms, you can add custom code as needed
                print("Opening the folder is not supported on this platform.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    def update_playlist_list(self):
        """
        Updates the playlist list widget with items from the 'Playlist' folder.

        This function clears the existing items in the list widget and populates it with the
        files found in the 'Playlist' folder.

        :return: None
        """
        try:
            # Clear the existing items in the list widget
            self.playlist_list.clear()

            # Path to the "Playlist" folder
            playlist_folder = os.path.abspath("Playlist")

            # Add files from the "Playlist" folder to the list widget
            for file in os.listdir(playlist_folder):
                item = QListWidgetItem(file)
                self.playlist_list.addItem(item)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            
    def focus_second_search_bar(self):
        """
        Sets the focus to the second search bar (self.stanza_search_bar)
        """
        self.stanza_search_bar.setFocus()

    def default(self):
        """
        Sets the default behavior for the application.

        If no 'max_stanza' is selected, it displays a message to prompt the user to
        select a Psalter. If 'max_stanza' is available, it populates the stanza search bar
        with the 'max_stanza' value.

        :return: None
        """
        if not self.max_stanza:
            self.additional_label.setText("Please Select a Psalter First")
            return
        self.stanza_search_bar.setText(self.max_stanza)
            

    def search_folder(self):
        """
        Searches for a Psalter folder matching the provided Psalter number and retrieves
        the associated verse value from the 'stanzas.db' database.

        If a matching folder is found, it sets various attributes such as folder path,
        Psalter name, and the 'max_stanza' value. If no matching folder is found, it
        displays an appropriate message.

        :return: None
        """
        try:
            partial_psalter = self.search_bar.text()
            if not partial_psalter:
                self.folder_name_label.setText("Please provide the Psalter number.")
                return
            sound_file_directory = 'good'

            matching_folders = []

            for folder in os.listdir(sound_file_directory):
                if os.path.isdir(os.path.join(sound_file_directory, folder)) and folder.startswith(partial_psalter):
                    matching_folders.append(folder)

            if matching_folders:
                self.folder_path = os.path.join(sound_file_directory, matching_folders[0])
                self.folder_name_label.setText(matching_folders[0])
                self.psalter_name = matching_folders[0]
                self.additional_label.setText("")

                psalter_name = self.psalter_name

                conn = sqlite3.connect('stanzas.db')
                cursor = conn.cursor()
                cursor.execute('SELECT verse_value FROM stanzas WHERE psalter_name = ?', (psalter_name,))

                # Fetch all the rows from the result
                rows = cursor.fetchall()
                verse_value=str(rows[0][0])
                self.max_stanza = verse_value
            else:
                self.folder_name_label.setText("Psalter not found.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    def combine_segments(self):
        """
        Combines audio segments for a specified Psalter with a specific verse count.
        
        This function takes user input for the Psalter number, stanza count, and search text.
        It then combines audio segments based on the user's request, creates or retrieves the 
        corresponding Psalter folder, saves the combined audio, creates shortcut links, and 
        updates the playlist. It handles different user inputs and platform-specific 
        commands for macOS and Windows.

        :return: None
        """
        try:
            if self.stanza_search_bar.text().isdigit():
                #Verify if Psalter search are left blank
                if not self.psalter_name:
                    self.additional_label.setText("Input Psalter to proceed")
                    return
                name_psalter = self.psalter_name

                #Verify if stanzas are left blank
                if not self.stanza_search_bar.text():
                    self.additional_label.setText("Input stanzas to proceed")
                    return
                elif not self.search_bar.text():
                    self.additional_label.setText("Search Psalter Number First")
                    return
                elif int(self.stanza_search_bar.text()) > int(self.max_stanza):
                    self.additional_label.setText(f"Stanzas should be less than or\nor equal to {self.max_stanza}")
                    return
                no_of_stanzas = int(self.stanza_search_bar.text())


                #Check if the folder associated with that psalter exists; if it doesn't, create the folder.
                Psalter_dir= os.path.join('Psalter', name_psalter)
                if not os.path.exists(Psalter_dir):
                    os.mkdir(Psalter_dir)

                #this will be the new name of the psalter that is requested by the user with specific verse
                psalter_verse = f"{name_psalter}({no_of_stanzas} verse).mp3"

                #This will check whether the requested psalter with a specific verse has already been created; if not, it will proceed to create it.
                direct_path = os.path.join(Psalter_dir, psalter_verse)
                if not os.path.exists(direct_path):
                    #Retrieve the path of 'good' > 'psalter_name' to use for iterating through the files in that folder.
                    path = self.folder_path
                    files = os.listdir(path)

                    #retrieve the mp3 files only and put it in 'mp3_files' list
                    mp3_files = [file for file in files if file.lower().endswith(".mp3")]
                    mp3_files = sorted(mp3_files)   
                    #initialize empty audio
                    combined_audio = AudioSegment.empty()

                    #iterate through the mp3_files
                    for mp3_file in mp3_files:
                        mp3_path = os.path.join(path, mp3_file)

                        #proceed with combining the audio with specific verse
                        audio_segment = AudioSegment.from_mp3(mp3_path)
                        if mp3_file == "2. verse.mp3":
                            for i in range(no_of_stanzas):
                                combined_audio += audio_segment.fade_out(300) + AudioSegment.silent(400)
                        elif mp3_file == "3. outro.mp3":
                            combined_audio += audio_segment.fade_in(200).fade_out(300) + AudioSegment.silent(400)
                        # Combine the segment with the existing combined audio
                        else:
                            combined_audio += audio_segment.fade_out(300) + AudioSegment.silent(400)
                    #save the combined audio with the direct path where it is located in the "Psalter" Mainfolder
                    combined_audio.export(direct_path, format="mp3",tags={'title': psalter_verse})

                    #Display a message to the user indicating that the requested psalter is already available
                #These paths will be utilized to generate shortcut link files for the audio in the Playlist Folder.
                # As a result, all the psalms requested by users will be accessible in the playlist folder,
                # making it easy to drag and drop files into VLC
                original_location = os.path.abspath(direct_path)
                symlink = os.path.join(os.path.abspath("Playlist"), psalter_verse)

                #This check ensures the flexibility of the app, adapting to the user's desktop environment, 
                # whether it's macOS or Windows.
                if not os.path.exists(symlink):
                    if platform.system() == "Darwin":
                        subprocess.run(['ln', '-s', original_location, symlink])
                    elif platform.system() == "Windows":
                        subprocess.run(['mklink', '/H', symlink, original_location], shell=True)
                    self.additional_label.setText("Selected psalter audio \nadded to the playlist!")
                    self.update_playlist_list()
                else:
                    self.additional_label.setText("Selected psalter audio \nALREADY added to the \nplaylist!")
            else:
                self.additional_label.setText("Please enter a valid \nPsalter number.")
                self.stanza_search_bar.setText("")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    def clear_playlist_folder(self):
        """
        Clears all files in the 'Playlist' folder.

        This function locates and removes all files within the 'Playlist' folder, leaving
        the folder itself intact. Any errors encountered during the file removal process
        are logged or printed.

        :return: None
        """
        try:
            # Path to the "Playlist" folder
            playlist_folder = os.path.abspath("Playlist")

            # Remove all files in the "Playlist" folder
            for file in os.listdir(playlist_folder):
                file_path = os.path.join(playlist_folder, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Error: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioCombinerApp()
    window.show()
    sys.exit(app.exec_())
