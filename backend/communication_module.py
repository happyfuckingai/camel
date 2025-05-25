import sqlite3
import requests
from typing import Tuple, Optional
from datetime import datetime

class CommunicationModule:
    """HappyAI Backend Communication Module"""
    
    def __init__(self):
        """Initialize with SQLite context database"""
        self.db_connection = sqlite3.connect('context.db')
        self._init_db()
        
    def _init_db(self):
        """Initialize database tables"""
        self.db_connection.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                user_input TEXT,
                intent TEXT,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_connection.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task_id TEXT,
                description TEXT,
                status TEXT,
                result TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_connection.commit()

    def handle_user_input(self, input_text: str) -> Tuple[str, Optional[str]]:
        """Main entry point for handling user input"""
        intent = self._detect_intent(input_text)
        
        if intent == "task":
            task_id = self._create_camel_task(input_text)
            self._log_conversation(input_text, intent, f"Task created: {task_id}")
            return ("Toppen, jag fixar det", task_id)
        else:
            response = self._generate_chat_response(input_text)
            self._log_conversation(input_text, intent, response)
            return (response, None)

    def _detect_intent(self, text: str) -> str:
        """Determine if input is a task or casual conversation"""
        task_keywords = ["boka", "schedule", "möte", "meeting", "påminn", "remind"]
        if any(keyword in text.lower() for keyword in task_keywords):
            return "task"
        return "chat"

    def _create_camel_task(self, description: str) -> str:
        """Create task in Camel AI system"""
        # TODO: Replace with actual Camel API integration
        task_id = f"task_{hash(description)}"
        self.db_connection.execute(
            "INSERT INTO tasks (task_id, description, status) VALUES (?, ?, ?)",
            (task_id, description, "pending"))
        self.db_connection.commit()
        return task_id

    def _generate_chat_response(self, text: str) -> str:
        """Generate response for casual conversation"""
        # TODO: Integrate with Gemma LLM
        return f"Jag hörde att du sa: {text}"

    def handle_callback(self, task_id: str, result: str) -> str:
        """Handle task completion callback from Camel"""
        self.db_connection.execute(
            "UPDATE tasks SET status = ?, result = ? WHERE task_id = ?",
            ("completed", result, task_id))
        self.db_connection.commit()
        return self._generate_summary(task_id)

    def _log_conversation(self, input_text: str, intent: str, response: str):
        """Log conversation to database"""
        self.db_connection.execute(
            "INSERT INTO conversations (user_input, intent, response) VALUES (?, ?, ?)",
            (input_text, intent, response))
        self.db_connection.commit()

    def _generate_summary(self, task_id: str) -> str:
        """Generate summary of task and related conversations"""
        task = self.db_connection.execute(
            "SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        conversations = self.db_connection.execute(
            "SELECT * FROM conversations WHERE user_input LIKE ?",
            (f"%{task[2]}%",)).fetchall()
        
        summary = f"Task Summary:\nID: {task_id}\nDescription: {task[2]}\n"
        summary += f"Result: {task[4]}\n\nRelated Conversations:\n"
        summary += "\n".join(f"- {conv[1]}" for conv in conversations)
        return summary

if __name__ == "__main__":
    # Example usage
    module = CommunicationModule()
    print(module.handle_user_input("Boka ett möte med Anna imorgon kl 10"))