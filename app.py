import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import google.generativeai as genai
import os
import pyttsx3
import threading

api_key = " "

# Check if API key is provided
if not api_key:
    raise ValueError("No Gemini API key found. Set GEMINI_API_KEY environment variable or update the script.")

# Configure GenAI with the API key
genai.configure(api_key=api_key)

# Initialize the Gemini model
gemini_model = genai.GenerativeModel("models/gemini-1.5-flash")

# Initialize TTS engine
tts_engine = pyttsx3.init()
tts_playing = False
stop_event = threading.Event()

# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

# Function to chunk text using LangChain
def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return [Document(page_content=chunk) for chunk in chunks]

# Function to process document with Gemini
def process_document_with_gemini(documents):
    model = genai.GenerativeModel("gemini-1.5-flash")
    system_prompt = """
    You are a contract interpreter. Given a document, extract exactly these four categories:
    - Key Clauses: Summarize the main clauses in 1-2 sentences each, focusing on what the document is really saying.
    - Risks: Identify potential pitfalls, such as termination clauses or confidentiality traps, in 1-2 sentences each.
    - Unusual Terms: Highlight non-standard phrasing or hidden obligations, in 1-2 sentences each.
    - Actionable Insights: Provide specific actions or checks to perform before signing, in 1-2 sentences each.
    Use bullet points (starting with '*') for each item under the respective category. Be concise and clear. Start each category with a header like '- Key Clauses:', '- Risks:', etc. Do not include any other information.
    """
    
    results = {"Key Clauses": [], "Risks": [], "Unusual Terms": [], "Actionable Insights": []}
    for doc in documents:
        try:
            response = model.generate_content(system_prompt + "\n\nDocument chunk:\n" + doc.page_content)
            if response.text:
                lines = response.text.split("\n")
                current_section = None
                for line in lines:
                    line = line.strip()
                    if line.startswith("- Key Clauses:"):
                        current_section = "Key Clauses"
                    elif line.startswith("- Risks:"):
                        current_section = "Risks"
                    elif line.startswith("- Unusual Terms:"):
                        current_section = "Unusual Terms"
                    elif line.startswith("- Actionable Insights:"):
                        current_section = "Actionable Insights"
                    elif line and current_section and line.startswith("* "):
                        results[current_section].append(line[2:].strip())
                    else:
                        print(f"Skipping unrecognized line: {line}")
        except Exception as e:
            print(f"Error processing chunk: {str(e)}")
            continue
    return results

# Function to process chat query with Gemini
def process_chat_query(query, documents):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        system_prompt = f"""
        You are a contract interpreter. Given the following document chunks and a user query, provide a concise answer based on the content.
        Document chunks: {''.join(doc.page_content for doc in documents)}
        User query: {query}
        Answer in 1-2 sentences. Do not include any other information.
        """
        response = model.generate_content(system_prompt)
        return response.text if response.text else "No response due to API quota limit. Please wait until midnight Pacific Time or upgrade your plan."
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return "Chat unavailable due to API quota limit. Please wait until midnight Pacific Time or upgrade your plan."

# Function to read text aloud
def read_aloud(text, app_instance):
    global tts_playing, stop_event
    if tts_playing and stop_event.is_set():
        return
    tts_engine.stop()
    stop_event.clear()
    tts_playing = True
    app_instance.play_button.config(text="⏸")
    tts_engine.say(text)
    tts_engine.runAndWait()
    if not stop_event.is_set():
        tts_playing = False
        app_instance.play_button.config(text="▶")

# Tkinter GUI
class PDFUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Contract Interpreter")
        self.root.geometry("600x750")
        self.root.configure(bg="#1e1e2e")

        # Bind window resize event
        self.root.bind("<Configure>", self.on_resize)

        # Gradient background
        self.canvas_bg = tk.Canvas(root, width=600, height=700, bg="#1e1e2e", highlightthickness=0)
        self.canvas_bg.pack(fill="both", expand=True)
        self.gradient = self.canvas_bg.create_rectangle(0, 0, 600, 700, fill="#1e1e2e", outline="")
        self.canvas_bg.tag_lower(self.gradient)

        # Style configuration
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12, "bold"), padding=8, background="#1c8d1c", foreground="black")
        style.map("TButton", background=[("active", "#7c4dff")], foreground=[("active", "white")])
        style.configure("TLabel", font=("Arial", 12), background="#1e1e2e", foreground="#a3bffa")
        style.configure("Custom.TButton", font=("Arial", 10), padding=4, background="#1d7bef")  # Smaller font and padding

        # Title
        self.title_label = ttk.Label(root, text="Auto Contract Interpreter", font=("Arial", 24, "bold"), foreground="#a3bffa")
        self.title_label.place(relx=0.5, rely=0.05, anchor="center")

        # Subtitle
        self.subtitle_label = ttk.Label(root, text="Upload a PDF contract to analyze", font=("Arial", 12))
        self.subtitle_label.place(relx=0.5, rely=0.12, anchor="center")

        # Upload button
        self.upload_button = ttk.Button(root, text="Upload PDF", command=self.upload_pdf, style="Custom.TButton")
        self.upload_button.place(relx=0.5, rely=0.20, anchor="center")

        # Status label
        self.status_label = ttk.Label(root, text="", foreground="#a3bffa")
        self.status_label.place(relx=0.5, rely=0.28, anchor="center")

        # Scrollable frame for results
        self.canvas = tk.Canvas(root, bg="#2a2e3a", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.place(relx=0.5, rely=0.40, anchor="n", relwidth=0.9, relheight=0.4)
        self.scrollbar.place(relx=0.95, rely=0.40, relheight=0.4, anchor="ne")

        # Result labels and text areas
        self.result_labels = {
            "Key Clauses": ttk.Label(self.scrollable_frame, text="Key Clauses", font=("Arial", 16, "bold"), foreground="#a3bffa"),
            "Risks": ttk.Label(self.scrollable_frame, text="Risks", font=("Arial", 16, "bold"), foreground="#a3bffa"),
            "Unusual Terms": ttk.Label(self.scrollable_frame, text="Unusual Terms", font=("Arial", 16, "bold"), foreground="#a3bffa"),
            "Actionable Insights": ttk.Label(self.scrollable_frame, text="Actionable Insights", font=("Arial", 16, "bold"), foreground="#a3bffa")
        }
        self.result_texts = {
            "Key Clauses": tk.Text(self.scrollable_frame, fg="black"),
            "Risks": tk.Text(self.scrollable_frame, fg="black"),
            "Unusual Terms": tk.Text(self.scrollable_frame, fg="black"),
            "Actionable Insights": tk.Text(self.scrollable_frame, fg="black")
        }

        # Chat interface
        self.chat_frame = ttk.Frame(root)
        self.chat_frame.place(relx=0.5, rely=0.82, anchor="n", relwidth=0.9)

        self.query_label = ttk.Label(self.chat_frame, text="Ask about the contract:", foreground="#a3bffa")
        self.query_label.pack(side="left", padx=5)

        self.query_entry = tk.Entry(self.chat_frame, width=100, font=("Arial", 10))
        self.query_entry.pack(side="left", padx=(0, 10), ipady=2)

        self.submit_button = ttk.Button(self.chat_frame, text="Submit Query", command=self.submit_query, style="Custom.TButton")
        self.submit_button.pack(side="right")
        self.chat_response = tk.Text(root, height=4, width=60, fg="black")
        self.chat_response.place(relx=0.5, rely=0.90, anchor="n", relwidth=0.9)

        # Play Audio button (moved to upper-right corner, smaller size)
        self.play_button = ttk.Button(root, text="Play Audio ▶", command=self.toggle_audio, style="Custom.TButton")
        self.play_button.place(relx=0.95, rely=0.05, anchor="ne")

        # Store documents and results
        self.documents = None
        self.raw_text = ""
        self.results = None

    def on_resize(self, event):
        # Update canvas and elements on window resize
        new_width = event.width - 30
        new_height = event.height - 250
        self.canvas_bg.config(width=event.width, height=event.height)
        self.canvas.config(width=new_width, height=new_height * 0.4)
        self.scrollbar.place(relx=0.95, rely=0.40, relheight=0.4, anchor="ne")
        self.chat_frame.place(relx=0.5, rely=0.82, anchor="n", relwidth=0.9)
        self.chat_response.place(relx=0.5, rely=0.90, anchor="n", relwidth=0.9)
        self.play_button.place(relx=0.95, rely=0.05, anchor="ne")
        self.canvas_bg.coords(self.gradient, 0, 0, event.width, event.height)

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                # Clear previous results
                for text_widget in self.result_texts.values():
                    text_widget.delete(1.0, tk.END)
                    text_widget.pack_forget()
                for label_widget in self.result_labels.values():
                    label_widget.pack_forget()
                self.chat_response.delete(1.0, tk.END)

                # Update status to indicate processing
                self.status_label.config(text="PDF uploaded, wait until analysis completes...")

                # Extract and chunk text
                self.raw_text = extract_text_from_pdf(file_path)
                self.documents = chunk_text(self.raw_text)

                # Process with Gemini
                self.results = process_document_with_gemini(self.documents)

                # Display results
                for category in ["Key Clauses", "Risks", "Unusual Terms", "Actionable Insights"]:
                    self.result_labels[category].pack(pady=10)
                    self.result_texts[category].pack(pady=5, fill="both", expand=True)
                    for item in self.results[category]:
                        self.result_texts[category].insert(tk.END, f"• {item}\n")
                    self.result_texts[category].config(state="disabled")

                # Update status after analysis
                self.status_label.config(text="Analysis done. Scroll down to see the results.")
            except Exception as e:
                self.status_label.config(text="")
                messagebox.showerror("Error", f"Failed to process PDF: {str(e)}")

    def submit_query(self):
        query = self.query_entry.get().strip()
        if query and self.documents:
            response = process_chat_query(query, self.documents)
            self.chat_response.delete(1.0, tk.END)
            self.chat_response.insert(tk.END, response)
            self.chat_response.config(state="disabled")
        else:
            self.chat_response.delete(1.0, tk.END)
            self.chat_response.insert(tk.END, "Please upload a PDF and enter a query.")
            self.chat_response.config(state="disabled")

    def toggle_audio(self):
        global tts_playing, stop_event
        if not tts_playing and self.results:
            stop_event.clear()
            text_to_read = ""
            for category in ["Key Clauses", "Risks", "Unusual Terms", "Actionable Insights"]:
                text_to_read += f"{category}:\n" + "\n".join(self.results.get(category, ["No data"])) + "\n\n"
            text_to_read += "Chat Response:\n" + self.chat_response.get(1.0, tk.END).strip()
            threading.Thread(target=read_aloud, args=(text_to_read, self), daemon=True).start()
        else:
            stop_event.set()
            tts_engine.stop()
            tts_playing = False
            self.play_button.config(text="Play Audio ▶")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFUploaderApp(root)
    root.mainloop()