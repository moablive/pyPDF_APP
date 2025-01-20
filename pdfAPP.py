import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon 
from pypdf import PdfReader, PdfWriter

class PDFCombinerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizador de PDFs")
        
        # Defina o ícone da janela (barra de título).
        # Supondo que o ícone esteja na mesma pasta e se chame "icone.png".
        self.setWindowIcon(QIcon("D:\!Developer\pyPDF_APP\pdf.ico"))

        self.setGeometry(300, 300, 600, 400)
        
        self.pdf_list = QListWidget()
        self.pdf_list.setSelectionMode(self.pdf_list.ExtendedSelection)
        
        # Permitir arrastar e soltar arquivos diretamente na lista
        self.pdf_list.setAcceptDrops(True)
        self.pdf_list.dragEnterEvent = self.dragEnterEvent
        self.pdf_list.dropEvent = self.dropEvent
        
        # Botões
        self.add_button = QPushButton("Adicionar PDFs")
        self.add_button.clicked.connect(self.add_pdfs)
        
        self.remove_button = QPushButton("Remover Selecionado")
        self.remove_button.clicked.connect(self.remove_selected)
        
        self.up_button = QPushButton("Mover Para Cima")
        self.up_button.clicked.connect(self.move_up)
        
        self.down_button = QPushButton("Mover Para Baixo")
        self.down_button.clicked.connect(self.move_down)
        
        self.combine_button = QPushButton("Combinar PDFs")
        self.combine_button.clicked.connect(self.combine_pdfs)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.pdf_list)
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        layout.addWidget(self.up_button)
        layout.addWidget(self.down_button)
        layout.addWidget(self.combine_button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def dragEnterEvent(self, event):
        """Reage ao arrastar arquivo sobre o QListWidget."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Reage ao soltar arquivo sobre o QListWidget."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(".pdf"):
                    self._add_pdf_pages_to_list(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def add_pdfs(self):
        """Abre diálogo para selecionar PDFs manualmente."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecione os PDFs",
            "",
            "Arquivos PDF (*.pdf)"
        )
        for path in file_paths:
            self._add_pdf_pages_to_list(path)
    
    def _add_pdf_pages_to_list(self, pdf_path):
        """
        Lê o PDF, verifica quantas páginas ele tem
        e adiciona um item na lista para cada página.
        """
        try:
            reader = PdfReader(pdf_path)
            num_paginas = len(reader.pages)
            for idx in range(num_paginas):
                # Cria texto para exibir no QListWidget
                display_text = f"{pdf_path} - Página {idx+1}"
                # Cria um item no QListWidget
                item = QListWidgetItem(display_text)
                # Vamos armazenar (pdf_path, indice_da_pagina) num "UserRole" 
                # para recuperarmos isso ao mesclar
                item.setData(Qt.UserRole, (pdf_path, idx))
                self.pdf_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro ao ler PDF",
                f"Não foi possível abrir {pdf_path}.\n\n{str(e)}"
            )
    
    def remove_selected(self):
        """Remove os itens selecionados da lista."""
        for item in self.pdf_list.selectedItems():
            self.pdf_list.takeItem(self.pdf_list.row(item))
    
    def move_up(self):
        """Move o item selecionado para cima na lista."""
        current_row = self.pdf_list.currentRow()
        if current_row > 0:
            item = self.pdf_list.takeItem(current_row)
            self.pdf_list.insertItem(current_row - 1, item)
            self.pdf_list.setCurrentRow(current_row - 1)

    def move_down(self):
        """Move o item selecionado para baixo na lista."""
        current_row = self.pdf_list.currentRow()
        if current_row < self.pdf_list.count() - 1 and current_row != -1:
            item = self.pdf_list.takeItem(current_row)
            self.pdf_list.insertItem(current_row + 1, item)
            self.pdf_list.setCurrentRow(current_row + 1)
    
    def combine_pdfs(self):
        """Combina, na ordem, cada página listada no QListWidget."""
        if self.pdf_list.count() == 0:
            QMessageBox.warning(self, "Aviso", "Nenhuma página para combinar.")
            return
        
        # Seleciona onde salvar o PDF combinado
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar PDF Combinado",
            "",
            "Arquivos PDF (*.pdf)"
        )
        
        if not output_path:
            return  # usuário cancelou
        
        try:
            pdf_writer = PdfWriter()
            
            # Adiciona cada "página" presente na lista (pode ser de PDFs diferentes)
            for i in range(self.pdf_list.count()):
                item = self.pdf_list.item(i)
                # Recupera os dados que guardamos lá em setData()
                pdf_path, page_idx = item.data(Qt.UserRole)
                
                # Lê novamente o PDF em questão (idealmente poderíamos otimizar)
                reader = PdfReader(pdf_path)
                page = reader.pages[page_idx]
                pdf_writer.add_page(page)

            with open(output_path, "wb") as out:
                pdf_writer.write(out)
            
            QMessageBox.information(self, "Sucesso", f"PDF combinado salvo em:\n{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao combinar PDFs:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    window = PDFCombinerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()