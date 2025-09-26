import gradio as gr
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os

# Import real agents
from agents.summarizer_agent import summarize
from agents.metadata_agent import extract_metadata
from agents.question_agent import answer

# Import custom modules with error handling
try:
    from enhanced_modules.safety_module import safety_validator, enhanced_content_filter, validate_request
    ENHANCED_SAFETY_AVAILABLE = True
except ImportError:
    print("Enhanced safety modules not available, using basic validation")
    ENHANCED_SAFETY_AVAILABLE = False
    
    # Create dummy safety validator
    class DummySafetyValidator:
        def __init__(self):
            self.max_file_size = 50 * 1024 * 1024
            
        def validate_file_safety(self, file_path, content):
            return True, "Basic validation only"
            
        def validate_text_content(self, text):
            return True, "Basic validation only"
            
        def validate_user_input(self, user_input, input_type="general"):
            return True, "Basic validation only"
            
        def sanitize_output(self, output):
            return output
            
        def log_security_event(self, event_type, details):
            pass
            
        def check_rate_limit(self, user_id, action="default"):
            return True
            
    class DummyContentFilter:
        def filter_document_content(self, content):
            return True, "Basic filtering", content, {}
    
    safety_validator = DummySafetyValidator()
    enhanced_content_filter = DummyContentFilter()
    
    def validate_request(func):
        return func  # No-op decorator

def extract_text_from_file(file_path: str) -> str:
    """Extract text from different file types"""
    try:
        if file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif file_path.lower().endswith('.pdf'):
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                return text
            except ImportError:
                return "Error: PyPDF2 not installed. Install with: pip install PyPDF2"
        
        elif file_path.lower().endswith('.docx'):
            try:
                import docx
                doc = docx.Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                return "Error: python-docx not installed. Install with: pip install python-docx"
        
        else:
            return "File format not supported"
            
    except Exception as e:
        return f"Error extracting text: {str(e)}"

class EnhancedDocumentUI:
    """Enhanced user interface with real AI agent integration"""
    
    def __init__(self):
        self.session_data = {}
        self.processing_history = []
        self.setup_theme()
    
    def setup_theme(self):
        """Setup custom theme and styling"""
        self.custom_css = """
        /* Modern, professional styling */
        .gradio-container {
            max-width: 1200px !important;
            margin: auto !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .main-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            margin: 20px;
            padding: 30px;
        }
        
        .header-section {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(45deg, #2196F3, #21CBF3);
            border-radius: 15px;
            color: white;
        }
        
        .upload-area {
            border: 3px dashed #2196F3;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            transition: all 0.3s ease;
        }
        
        .upload-area:hover {
            border-color: #1976D2;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            transform: translateY(-2px);
        }
        
        .result-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            border-left: 4px solid #2196F3;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .agent-status {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            margin: 5px 0;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-ready { background: #4CAF50; }
        .status-processing { background: #FF9800; }
        .status-complete { background: #2196F3; }
        .status-error { background: #f44336; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .chat-message {
            background: white;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #4CAF50;
        }
        
        .error-message {
            background: #ffebee;
            border: 1px solid #f44336;
            border-radius: 8px;
            padding: 15px;
            color: #c62828;
        }
        
        .metadata-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #2196F3, #21CBF3) !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 12px 30px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            transition: all 0.3s ease !important;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3) !important;
        }
        """
    
    @validate_request
    def process_document_enhanced(self, file, progress=gr.Progress()):
        """Enhanced document processing with real AI agents"""
        try:
            if not file:
                return (
                    "",
                    "",
                    "⚠️ No file uploaded",
                    self.get_agent_status_html("error"),
                    ""
                )
            
            progress(0.1, desc="Validating file...")
            
            # Safety validation
            try:
                with open(file.name, 'rb') as f:
                    file_content = f.read()
                
                filename_only = os.path.basename(file.name)
                
                # Check file size
                if len(file_content) > safety_validator.max_file_size:
                    return (
                        "",
                        "",
                        f"🚫 File too large: {len(file_content) // (1024*1024)}MB (max 50MB)",
                        self.get_agent_status_html("error"),
                        ""
                    )
                
                # Check file extension
                allowed_extensions = {'.pdf', '.txt', '.docx'}
                if not any(filename_only.lower().endswith(ext) for ext in allowed_extensions):
                    return (
                        "",
                        "",
                        f"🚫 File type not supported. Allowed: {', '.join(allowed_extensions)}",
                        self.get_agent_status_html("error"),
                        ""
                    )
                
                if not self.is_filename_safe(filename_only):
                    return (
                        "",
                        "",
                        "🚫 Filename contains invalid characters",
                        self.get_agent_status_html("error"),
                        ""
                    )
                    
            except Exception as e:
                return (
                    "",
                    "",
                    f"⚠️ File validation error: {str(e)}",
                    self.get_agent_status_html("error"),
                    ""
                )
            
            progress(0.2, desc="Extracting text from document...")
            
            # Extract text from file
            document_text = extract_text_from_file(file.name)
            
            if document_text.startswith("Error"):
                return (
                    "",
                    "",
                    f"⚠️ {document_text}",
                    self.get_agent_status_html("error"),
                    ""
                )
            
            # Content validation
            if ENHANCED_SAFETY_AVAILABLE:
                # The filter_document_content function returns 4 values: (is_safe, message, content, info)
                filter_result = enhanced_content_filter.filter_document_content(document_text)
                if len(filter_result) >= 4:
                    is_safe, safety_message, filtered_content, filter_info = filter_result
                elif len(filter_result) == 3:
                    is_safe, safety_message, filtered_content = filter_result
                    filter_info = {}
                else:
                    is_safe, safety_message = filter_result[:2]
                    filtered_content = document_text
                    filter_info = {}
                
                if not is_safe:
                    return (
                        "",
                        "",
                        f"🚫 Content validation failed: {safety_message}",
                        self.get_agent_status_html("error"),
                        ""
                    )
                
                # Use filtered content if available
                if filtered_content and filtered_content != document_text:
                    document_text = filtered_content
            
            progress(0.4, desc="Processing with Summarizer Agent...")
            
            # Generate summary using real agent
            try:
                summary_text = summarize(document_text)
            except Exception as e:
                summary_text = f"Error generating summary: {str(e)}"
            
            progress(0.7, desc="Processing with Metadata Agent...")
            
            # Extract metadata using real agent
            try:
                metadata = extract_metadata(document_text)
            except Exception as e:
                metadata = {
                    "title": f"Analysis of {filename_only}",
                    "author": "Unknown",
                    "date": "Unknown",
                    "keywords": ["document", "analysis"],
                    "error": f"Metadata extraction error: {str(e)}"
                }
            
            progress(0.9, desc="Finalizing results...")
            
            # Store in session for subsequent questions
            session_id = str(int(time.time()))
            self.session_data[session_id] = {
                "filename": file.name,
                "document_text": document_text,
                "summary": summary_text,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to history
            self.processing_history.append({
                "filename": filename_only,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "status": "success"
            })
            
            progress(1.0, desc="Complete!")
            
            return (
                self.format_summary_html(summary_text),
                self.format_metadata_html(metadata),
                "✅ Document processed successfully!",
                self.get_agent_status_html("complete"),
                session_id
            )
            
        except Exception as e:
            if ENHANCED_SAFETY_AVAILABLE:
                safety_validator.log_security_event("processing_error", {"error": str(e)})
            return (
                "",
                "",
                f"⚠️ Processing failed: {str(e)}",
                self.get_agent_status_html("error"),
                ""
            )
    
    def is_filename_safe(self, filename):
        """Improved filename safety check"""
        import re
        
        if not filename or filename.strip() == "":
            return False
        
        dangerous_chars = r'[<>"|?*]'
        if re.search(dangerous_chars, filename):
            return False
        
        if '..' in filename:
            return False
        
        if len(filename) > 255:
            return False
            
        return True
    
    @validate_request
    def answer_question_enhanced(self, question: str, session_state: str) -> str:
        """Enhanced question answering with real AI agent"""
        try:
            if not question.strip():
                return "❌ Please enter a question."
            
            if not session_state or session_state not in self.session_data:
                return "❌ No document loaded. Please upload a document first."
            
            # Validate user input
            is_safe, safety_message = safety_validator.validate_user_input(question, "question")
            if not is_safe:
                return f"🚫 Question validation failed: {safety_message}"
            
            # Get document context
            session_data = self.session_data[session_state]
            document_context = session_data.get("document_text", "")
            
            # Use real question agent
            try:
                ai_answer = answer(document_context, question)
                sanitized_answer = safety_validator.sanitize_output(ai_answer)
                return self.format_answer_html(question, sanitized_answer)
            except Exception as e:
                return f"⚠️ Question answering error: {str(e)}"
            
        except Exception as e:
            if ENHANCED_SAFETY_AVAILABLE:
                safety_validator.log_security_event("qa_error", {"error": str(e)})
            return f"⚠️ Question answering failed: {str(e)}"
    
    def format_summary_html(self, summary: str) -> str:
        """Format summary with HTML styling"""
        formatted_summary = summary.replace('\n', '<br>')
        return f"""
        <div class="result-card">
            <h3>📄 Document Summary</h3>
            <div style="line-height: 1.6; color: #333;">
                {formatted_summary}
            </div>
        </div>
        """
    
    def format_metadata_html(self, metadata: Dict) -> str:
        """Format metadata with HTML styling"""
        html_content = """
        <div class="metadata-card">
            <h3>📊 Document Metadata</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px;">
        """
        
        for key, value in metadata.items():
            if isinstance(value, list):
                value = ", ".join(value)
            
            html_content += f"""
                <div style="background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px;">
                    <strong>{key.replace('_', ' ').title()}:</strong><br>
                    <span style="font-size: 0.9em;">{value}</span>
                </div>
            """
        
        html_content += """
            </div>
        </div>
        """
        return html_content
    
    def format_answer_html(self, question: str, answer: str) -> str:
        """Format Q&A with HTML styling"""
        formatted_answer = answer.replace('\n', '<br>')
        return f"""
        <div class="chat-message">
            <div style="background: #e3f2fd; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                <strong>❓ Question:</strong> {question}
            </div>
            <div style="background: #f1f8e9; padding: 10px; border-radius: 8px;">
                <strong>🤖 AI Response:</strong><br>
                {formatted_answer}
            </div>
        </div>
        """
    
    def get_agent_status_html(self, status: str) -> str:
        """Get agent status HTML"""
        status_info = {
            "ready": ("🟢", "Agents Ready", "All AI agents are initialized and ready to process documents."),
            "processing": ("🟡", "Processing...", "AI agents are currently analyzing your document."),
            "complete": ("🔵", "Processing Complete", "All agents have successfully completed the analysis."),
            "error": ("🔴", "Error", "An error occurred during processing. Please try again.")
        }
        
        indicator, title, description = status_info.get(status, status_info["ready"])
        
        return f"""
        <div class="agent-status">
            <div class="status-indicator status-{status}"></div>
            <div>
                <strong>{indicator} {title}</strong><br>
                <small>{description}</small>
            </div>
        </div>
        """
    
    def get_processing_history_html(self) -> str:
        """Get processing history HTML"""
        if not self.processing_history:
            return "<p>No processing history yet.</p>"
        
        html = "<div class='history-container'><h4>📋 Recent Activity</h4>"
        for item in self.processing_history[-5:]:
            status_icon = "✅" if item["status"] == "success" else "⚠️"
            html += f"""
            <div class="history-item" style="padding: 8px; margin: 5px 0; background: #f8f9fa; border-radius: 6px;">
                {status_icon} {item['filename']} - {item['timestamp']}
            </div>
            """
        html += "</div>"
        return html
    
    def create_interface(self):
        """Create the enhanced Gradio interface"""
        with gr.Blocks(
            css=self.custom_css,
            title="Document AI Multi-Agent Assistant",
            theme=gr.themes.Base()
        ) as interface:
            
            # Header
            safety_status = "Enhanced Security" if ENHANCED_SAFETY_AVAILABLE else "Basic Mode"
            gr.HTML(f"""
                <div class="header-section">
                    <h1>🤖 Document AI Multi-Agent Assistant</h1>
                    <p>Advanced document analysis powered by multiple specialized AI agents</p>
                    <p style="font-size: 0.9em; opacity: 0.8;">
                        Upload documents • Get intelligent summaries • Extract metadata • Ask questions
                    </p>
                    <div style="font-size: 0.8em; opacity: 0.7; margin-top: 10px;">
                        Security Mode: {safety_status} | AI Agents: Active
                    </div>
                </div>
            """)
            
            # Main interface
            with gr.Row():
                with gr.Column(scale=2):
                    # File upload section
                    gr.HTML("<h3>📁 Document Upload</h3>")
                    file_upload = gr.File(
                        label="Select Document",
                        file_types=[".pdf", ".txt", ".docx"],
                        elem_classes=["upload-area"]
                    )
                    
                    process_btn = gr.Button(
                        "🚀 Process Document",
                        variant="primary",
                        elem_classes=["btn-primary"]
                    )
                    
                    # Status display
                    agent_status = gr.HTML(self.get_agent_status_html("ready"))
                    status_display = gr.Textbox(
                        label="Status",
                        value="Ready to process documents",
                        interactive=False
                    )
                
                with gr.Column(scale=3):
                    # Results tabs
                    with gr.Tabs():
                        with gr.Tab("📄 Summary"):
                            summary_output = gr.HTML("")
                        
                        with gr.Tab("📊 Metadata"):
                            metadata_output = gr.HTML("")
                        
                        with gr.Tab("❓ Q&A"):
                            with gr.Column():
                                question_input = gr.Textbox(
                                    label="Ask a question about the document",
                                    placeholder="What is this document about?",
                                    lines=2
                                )
                                ask_btn = gr.Button("Ask Question", variant="secondary")
                                answer_output = gr.HTML("")
                        
                        with gr.Tab("📋 History"):
                            history_output = gr.HTML(self.get_processing_history_html())
            
            # Hidden components for state management
            session_state = gr.Textbox(visible=False)
            
            # Event handlers
            process_btn.click(
                fn=self.process_document_enhanced,
                inputs=[file_upload],
                outputs=[summary_output, metadata_output, status_display, agent_status, session_state]
            ).then(
                fn=lambda: self.get_processing_history_html(),
                outputs=[history_output]
            )
            
            ask_btn.click(
                fn=self.answer_question_enhanced,
                inputs=[question_input, session_state],
                outputs=[answer_output]
            )
            
            # Footer
            gr.HTML("""
                <div style="text-align: center; padding: 20px; color: #666; border-top: 1px solid #eee; margin-top: 40px;">
                    <p>🔒 Your data is processed securely with built-in safety measures</p>
                    <p style="font-size: 0.8em;">Real AI agents • Enhanced security • Content filtering</p>
                </div>
            """)
        
        return interface


def launch_enhanced_ui():
    """Launch the enhanced user interface"""
    ui = EnhancedDocumentUI()
    interface = ui.create_interface()
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True,
        quiet=False,
        inbrowser=True
    )


if __name__ == "__main__":
    launch_enhanced_ui()