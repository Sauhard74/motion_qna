import json
import random
from typing import List, Dict, Any, Optional
import os
import numpy as np
import re
import math

import nltk
from transformers import AutoTokenizer, AutoModel, pipeline
from sentence_transformers import SentenceTransformer
import torch
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings
from app.models.question import QuestionType

# Import custom tokenizer
from app.services.custom_tokenizer import custom_sent_tokenize, custom_tokenize, get_stopwords

# Try to import NLTK, but always use our custom tokenizer for sentence splitting
try:
    import nltk
    nltk.download('stopwords')
    from nltk.corpus import stopwords
    STOPWORDS = set(stopwords.words('english'))
    
    # We'll always use our custom tokenizer regardless of NLTK availability
    # to avoid punkt_tab issues
    sent_tokenize = custom_sent_tokenize
    word_tokenize = custom_tokenize
except ImportError:
    # Fallback if NLTK is not installed
    STOPWORDS = set(get_stopwords())
    sent_tokenize = custom_sent_tokenize
    word_tokenize = custom_tokenize

try:
    from transformers import AutoTokenizer, AutoModel, pipeline
    from sentence_transformers import SentenceTransformer
    import torch
    from sklearn.metrics.pairwise import cosine_similarity
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class AIService:
    """Service for AI-powered operations like hint and solution generation."""
    
    def __init__(self):
        """Initialize the AI service."""
        self.use_transformers = TRANSFORMERS_AVAILABLE and settings.USE_AI_MODELS
        self.device = "cuda" if TRANSFORMERS_AVAILABLE and torch.cuda.is_available() else "cpu"
        
        # Check if we should use models or fallback to template-based generation
        if settings.USE_AI_MODELS and self.use_transformers:
            try:
                # Load sentence transformer model for embeddings and similarity
                self.embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2', device=self.device)
                
                # Set up text generation pipeline for hints and solutions
                self.generator = pipeline(
                    "text-generation",
                    model="distilgpt2",
                    device=0 if self.device == "cuda" else -1
                )
                
                # Create classification embeddings for question types
                self.question_type_embeddings = self._create_question_type_embeddings()
                
                # Knowledge database - embeddings of concept explanations
                self.knowledge_base = self._load_knowledge_base()
                
                print("AI models loaded successfully")
            except Exception as e:
                print(f"Error loading AI models: {e}")
                self.use_transformers = False
        else:
            self.use_transformers = False
            print("Using template-based generation (no transformers)")
    
    def _create_question_type_embeddings(self) -> Dict[QuestionType, np.ndarray]:
        """Create embeddings for different question types"""
        type_descriptions = {
            QuestionType.MATH: "Mathematics problem involving equations, calculations, algebra, geometry, or numerical analysis",
            QuestionType.PHYSICS: "Physics problem involving forces, motion, energy, mechanics, electricity, or thermodynamics",
            QuestionType.CHEMISTRY: "Chemistry problem involving elements, compounds, reactions, bonds, or molecular structures",
            QuestionType.BIOLOGY: "Biology problem involving cells, organisms, genetics, evolution, ecology, or physiology",
            QuestionType.COMPUTER_SCIENCE: "Computer science problem involving algorithms, data structures, programming, complexity, or computational theory",
            QuestionType.OTHER: "General knowledge problem not specific to math, physics, chemistry, biology, or computer science"
        }
        
        embeddings = {}
        for qtype, description in type_descriptions.items():
            embeddings[qtype] = self.embedding_model.encode(description)
        
        return embeddings
    
    def _load_knowledge_base(self) -> Dict[str, np.ndarray]:
        """Load knowledge base with concept explanations"""
        # This would normally load from a database or file
        # Here we're creating a simple in-memory knowledge base
        knowledge_base = {
            "algebra": "Algebra is a branch of mathematics dealing with symbols and the rules for manipulating these symbols.",
            "force": "Force is any interaction that, when unopposed, will change the motion of an object.",
            "chemical_bond": "A chemical bond is a lasting attraction between atoms that enables the formation of molecules.",
            "cell_division": "Cell division is the process by which a parent cell divides into two or more daughter cells.",
            "algorithm": "An algorithm is a step-by-step procedure for calculations or problem-solving operations."
        }
        
        # Create embeddings for each concept
        embedded_knowledge = {}
        for concept, explanation in knowledge_base.items():
            embedded_knowledge[concept] = {
                "explanation": explanation,
                "embedding": self.embedding_model.encode(explanation)
            }
        
        return embedded_knowledge
    
    def analyze_question(self, question_content: str) -> Dict[str, Any]:
        """
        Analyze a question to determine its type, difficulty, and structure using BERT.
        
        Args:
            question_content: The content of the question to analyze.
            
        Returns:
            A dictionary with analysis results.
        """
        if not self.use_transformers:
            return self._analyze_question_with_templates(question_content)
        
        try:
            # Encode the question
            question_embedding = self.embedding_model.encode(question_content)
            
            # Determine question type using cosine similarity
            similarities = {}
            for qtype, type_embedding in self.question_type_embeddings.items():
                similarity = cosine_similarity(
                    [question_embedding], 
                    [type_embedding]
                )[0][0]
                similarities[qtype] = similarity
            
            # Get the question type with highest similarity
            question_type = max(similarities, key=similarities.get)
            
            # Extract relevant concepts from the knowledge base
            relevant_concepts = self._find_relevant_concepts(question_embedding)
            
            # Calculate complexity metrics
            sentences = custom_sent_tokenize(question_content)
            words = word_tokenize(question_content.lower())
            avg_sentence_length = len(words) / max(1, len(sentences))
            
            # Calculate difficulty score (1-5) based on various metrics
            difficulty_factors = [
                min(len(words) / 25, 2),  # Length factor
                min(avg_sentence_length / 10, 1.5),  # Sentence complexity
                min(1.5, 1 + len(relevant_concepts) * 0.3)  # Concept density
            ]
            difficulty_score = min(5, sum(difficulty_factors))
            
            # Extract keywords using embeddings for key phrases
            keywords = self._extract_keywords_advanced(question_content)
            
            return {
                "type": question_type,
                "difficulty_score": difficulty_score,
                "word_count": len(words),
                "sentence_count": len(sentences),
                "keywords": keywords,
                "relevant_concepts": relevant_concepts,
                "original_content": question_content  # Store the original content
            }
        except Exception as e:
            print(f"Error in BERT analysis: {e}")
            # Fallback to template-based analysis
            return self._analyze_question_with_templates(question_content)
    
    def _analyze_question_with_templates(self, question_content: str) -> Dict[str, Any]:
        """Fallback to template-based question analysis"""
        # Simple keyword-based analysis for the prototype
        question_lower = question_content.lower()
        
        # Determine question type
        question_type = QuestionType.OTHER
        # Better pattern matching for math problems
        if any(kw in question_lower for kw in ["solve", "equation", "calculate", "value", "find x", "find the value", "=", "equals"]):
            question_type = QuestionType.MATH
        elif any(kw in question_lower for kw in ["force", "energy", "motion", "velocity"]):
            question_type = QuestionType.PHYSICS
        elif any(kw in question_lower for kw in ["element", "compound", "molecule", "reaction"]):
            question_type = QuestionType.CHEMISTRY
        elif any(kw in question_lower for kw in ["cell", "organism", "species", "gene"]):
            question_type = QuestionType.BIOLOGY
        elif any(kw in question_lower for kw in ["algorithm", "code", "program", "function"]):
            question_type = QuestionType.COMPUTER_SCIENCE
        
        # Estimate difficulty based on question length and complexity
        words = question_lower.split()
        difficulty_score = min(len(words) / 20, 3)  # Simple heuristic
        
        # Use custom sentence tokenizer to avoid nltk.sent_tokenize issues
        sentences = custom_sent_tokenize(question_content)
        
        return {
            "type": question_type,
            "difficulty_score": difficulty_score,
            "word_count": len(words),
            "sentence_count": len(sentences),
            "keywords": self._extract_keywords(question_content),
            "relevant_concepts": [],
            "original_content": question_content  # Store the original content
        }
    
    def _find_relevant_concepts(self, question_embedding: np.ndarray, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Find relevant concepts from the knowledge base using embedding similarity"""
        relevant_concepts = []
        
        for concept, data in self.knowledge_base.items():
            concept_embedding = data["embedding"]
            similarity = cosine_similarity([question_embedding], [concept_embedding])[0][0]
            
            if similarity > threshold:
                relevant_concepts.append({
                    "concept": concept,
                    "explanation": data["explanation"],
                    "relevance": float(similarity)
                })
        
        # Sort by relevance (highest first)
        relevant_concepts.sort(key=lambda x: x["relevance"], reverse=True)
        return relevant_concepts[:3]  # Return top 3 most relevant concepts
    
    def _extract_keywords_advanced(self, text: str) -> List[str]:
        """Extract important keywords using embeddings"""
        stop_words = set(stopwords.words('english'))
        
        # Get candidate keywords (non-stopwords)
        words = word_tokenize(text.lower())
        candidates = [word for word in words if word not in stop_words and len(word) > 3]
        
        if not candidates:
            return self._extract_keywords(text)  # Fallback
        
        # Get embeddings for each candidate
        try:
            candidate_embeddings = self.embedding_model.encode(candidates)
            text_embedding = self.embedding_model.encode(text)
            
            # Calculate importance scores based on similarity to full text
            similarities = cosine_similarity([text_embedding], candidate_embeddings)[0]
            
            # Pair candidates with their importance scores
            keyword_scores = list(zip(candidates, similarities))
            
            # Sort by importance score (descending)
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top keywords
            return [keyword for keyword, _ in keyword_scores[:10]]
        except:
            return self._extract_keywords(text)  # Fallback
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text (fallback method)."""
        # Simple keyword extraction for the prototype
        words = text.lower().split()
        stopwords_set = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about"}
        keywords = [word for word in words if word not in stopwords_set and len(word) > 3]
        return keywords[:10]  # Return top 10 keywords
    
    def generate_hints(self, question_content: str, num_hints: int = 1, max_level: int = 3) -> List[Dict[str, Any]]:
        """
        Generate hints for a question using transformer models or templates.
        
        Args:
            question_content: The content of the question.
            num_hints: Number of hints to generate.
            max_level: Maximum hint level (difficulty).
            
        Returns:
            A list of hint dictionaries.
        """
        # Analyze the question to get context
        question_analysis = self.analyze_question(question_content)
        
        if self.use_transformers and hasattr(self, 'generator'):
            try:
                return self._generate_hints_with_transformers(question_content, question_analysis, num_hints, max_level)
            except Exception as e:
                print(f"Error generating hints with transformers: {e}")
                # Fallback to template-based generation
        
        # Use template-based hint generation
        return self._generate_hints_with_templates(question_analysis, num_hints, max_level)
    
    def _generate_hints_with_transformers(self, question_content: str, question_analysis: Dict[str, Any], 
                                         num_hints: int, max_level: int) -> List[Dict[str, Any]]:
        """Generate hints using transformer models"""
        hints = []
        question_type = question_analysis["type"]
        keywords = question_analysis["keywords"]
        relevant_concepts = question_analysis.get("relevant_concepts", [])
        
        # Create prompts for each hint level
        prompts = []
        for level in range(1, min(num_hints + 1, max_level + 1)):
            difficulty = "subtle" if level == 1 else "more direct" if level == 2 else "very specific"
            
            # Build context from relevant concepts
            context = ""
            if relevant_concepts and level > 1:
                context = f"Consider these concepts: {', '.join([c['concept'] for c in relevant_concepts[:2]])}. "
            
            # Create prompt based on question type
            if question_type == QuestionType.MATH:
                prompt = f"For the math problem: '{question_content}', provide a {difficulty} hint without giving away the answer. {context}"
            elif question_type == QuestionType.PHYSICS:
                prompt = f"For the physics problem: '{question_content}', provide a {difficulty} hint about relevant principles. {context}"
            else:
                prompt = f"For this problem: '{question_content}', give a {difficulty} hint that helps solve it. {context}"
            
            prompts.append(prompt)
        
        # Generate hints for each prompt
        for i, prompt in enumerate(prompts):
            level = i + 1
            try:
                # Generate hint with the model
                outputs = self.generator(prompt, max_length=100, num_return_sequences=1, temperature=0.7)
                hint_text = outputs[0]['generated_text'].replace(prompt, "").strip()
                
                # Clean up the hint
                hint_sentences = custom_sent_tokenize(hint_text)
                if hint_sentences:
                    hint_text = hint_sentences[0]  # Take first sentence
                
                hints.append({
                    "content": hint_text,
                    "level": level
                })
            except Exception as e:
                # Fallback for this specific hint
                print(f"Error generating hint level {level}: {e}")
                hint_templates = self._get_hint_templates(question_type)
                hint_template = random.choice(hint_templates[min(level, len(hint_templates)) - 1])
                hint_text = hint_template
                
                # Replace placeholders with keywords
                for j, keyword in enumerate(keywords[:3]):
                    placeholder = f"{{keyword{j+1}}}"
                    if placeholder in hint_text:
                        hint_text = hint_text.replace(placeholder, keyword)
                
                hints.append({
                    "content": hint_text,
                    "level": level
                })
        
        return hints
    
    def _generate_hints_with_templates(self, question_analysis: Dict[str, Any], 
                                      num_hints: int, max_level: int) -> List[Dict[str, Any]]:
        """Generate hints using templates"""
        hints = []
        question_type = question_analysis["type"]
        keywords = question_analysis["keywords"]
        
        hint_templates = self._get_hint_templates(question_type)
        
        for i in range(1, min(num_hints + 1, max_level + 1)):
            hint_template = random.choice(hint_templates[min(i, len(hint_templates)) - 1])
            hint_text = hint_template
            
            # Replace placeholders with keywords
            for j, keyword in enumerate(keywords[:3]):
                placeholder = f"{{keyword{j+1}}}"
                if placeholder in hint_text:
                    hint_text = hint_text.replace(placeholder, keyword)
            
            hints.append({
                "content": hint_text,
                "level": i
            })
        
        return hints
    
    def _get_hint_templates(self, question_type: QuestionType) -> List[List[str]]:
        """Get hint templates for a specific question type and difficulty level."""
        # Templates are grouped by difficulty level (1, 2, 3)
        if question_type == QuestionType.MATH:
            return [
                # Level 1 (easy) hints
                [
                    "Think about isolating the variable by moving all other terms to the opposite side of the equation.",
                    "Remember that you can add or subtract the same value from both sides of an equation.",
                    "Start by identifying what operation you need to perform to isolate the variable.",
                ],
                # Level 2 (medium) hints
                [
                    "To solve for the variable, you need to perform the inverse operation of what's being applied to it.",
                    "If you have x + a = b, you can subtract a from both sides to isolate x.",
                    "If you have ax = b, you can divide both sides by a to isolate x.",
                ],
                # Level 3 (hard) hints
                [
                    "Rearrange the equation step by step, keeping track of what you do to maintain the equality.",
                    "After isolating the variable on one side, simplify the expression on the other side to get your answer.",
                    "Check your answer by substituting it back into the original equation to verify it's correct.",
                ]
            ]
        elif question_type == QuestionType.PHYSICS:
            return [
                [
                    "Think about the relevant physical laws.",
                    "Consider the units of each quantity.",
                    "Identify the forces acting on the object.",
                ],
                [
                    "Use the equation for {keyword1} in this problem.",
                    "Convert units appropriately before calculation.",
                    "Draw a free-body diagram to visualize the problem.",
                ],
                [
                    "Apply the conservation of {keyword1} principle.",
                    "Consider both initial and final states of the system.",
                    "This problem requires integrating the {keyword1} over time.",
                ]
            ]
        else:
            # Generic templates for other question types
            return [
                [
                    "Start by identifying the key concepts.",
                    "Consider what the question is asking for.",
                    "Look for clues in the wording of the question.",
                ],
                [
                    "Break down the problem into smaller parts.",
                    "Focus on the relationship between {keyword1} and {keyword2}.",
                    "Try applying the concept of {keyword1} to this problem.",
                ],
                [
                    "This problem involves advanced application of {keyword1}.",
                    "Consider the implications of combining {keyword1} with {keyword2}.",
                    "Apply the theoretical framework to solve this problem.",
                ]
            ]
    
    def generate_solution(self, question_content: str, step_by_step: bool = True) -> Dict[str, Any]:
        """
        Generate a solution for a question using transformer models or templates.
        
        Args:
            question_content: The content of the question.
            step_by_step: Whether to generate a step-by-step solution.
            
        Returns:
            A dictionary with the solution and optional steps.
        """
        # First, try to solve it as a basic equation regardless of the question analysis
        equation_solution = self._solve_basic_equation(question_content)
        if equation_solution:
            return equation_solution
            
        # If it's not a basic equation, analyze the question and proceed normally
        question_analysis = self.analyze_question(question_content)
        
        if self.use_transformers and hasattr(self, 'generator'):
            try:
                return self._generate_solution_with_transformers(question_content, question_analysis, step_by_step)
            except Exception as e:
                print(f"Error generating solution with transformers: {e}")
                # Fallback to template-based generation
        
        # Use template-based solution generation
        return self._generate_solution_with_templates(question_analysis, step_by_step)
    
    def _generate_solution_with_transformers(self, question_content: str, 
                                           question_analysis: Dict[str, Any], 
                                           step_by_step: bool) -> Dict[str, Any]:
        """Generate solution using transformer models"""
        question_type = question_analysis["type"]
        relevant_concepts = question_analysis.get("relevant_concepts", [])
        
        # Build context from relevant concepts
        context = ""
        if relevant_concepts:
            concepts = ", ".join([c["concept"] for c in relevant_concepts[:2]])
            context = f" Relevant concepts: {concepts}."
        
        # Create prompt based on question type and step_by_step preference
        solution_prompt = f"Solve this problem:{context} '{question_content}'"
        if step_by_step:
            solution_prompt += " Explain the solution step by step with detailed reasoning."
        
        try:
            # Generate solution with the model
            outputs = self.generator(solution_prompt, max_length=300, num_return_sequences=1, temperature=0.7)
            solution_text = outputs[0]['generated_text'].replace(solution_prompt, "").strip()
            
            # Process for step-by-step if requested
            steps = None
            content = solution_text
            
            if step_by_step:
                # Try to parse steps from the generated text
                try:
                    content_parts = solution_text.split("Step 1:")
                    if len(content_parts) > 1:
                        content = content_parts[0].strip()
                        steps_text = "Step 1:" + content_parts[1]
                        steps = steps_text
                    else:
                        # If no clear steps, split by sentences
                        sentences = custom_sent_tokenize(solution_text)
                        if len(sentences) > 3:
                            content = sentences[0]
                            steps = "\n".join([f"Step {i+1}: {s}" for i, s in enumerate(sentences[1:])])
                        else:
                            steps = None
                except:
                    steps = None
            
            return {
                "content": content,
                "steps": steps
            }
        except Exception as e:
            print(f"Error in solution generation: {e}")
            # Fallback to template-based generation
            return self._generate_solution_with_templates(question_analysis, step_by_step)
    
    def _generate_solution_with_templates(self, question_analysis: Dict[str, Any], 
                                         step_by_step: bool) -> Dict[str, Any]:
        """Generate solution using templates"""
        question_type = question_analysis["type"]
        keywords = question_analysis["keywords"]
        question_content = question_analysis.get("original_content", "")
        
        # Get a solution template (fallback)
        solution_template = self._get_solution_template(question_type)
        
        # Replace placeholders with keywords
        solution_text = solution_template
        for i, keyword in enumerate(keywords[:3]):
            placeholder = f"{{keyword{i+1}}}"
            if placeholder in solution_text:
                solution_text = solution_text.replace(placeholder, keyword)
        
        # Generate steps if step_by_step is True
        steps = None
        if step_by_step:
            step_templates = self._get_step_templates(question_type)
            steps_list = []
            for i, step_template in enumerate(step_templates):
                step_text = step_template
                for j, keyword in enumerate(keywords[:3]):
                    placeholder = f"{{keyword{j+1}}}"
                    if placeholder in step_text:
                        step_text = step_text.replace(placeholder, keyword)
                steps_list.append(f"Step {i+1}: {step_text}")
            steps = "\n".join(steps_list)
        
        return {
            "content": solution_text,
            "steps": steps
        }
        
    def _solve_basic_equation(self, question_content: str) -> Optional[Dict[str, Any]]:
        """Attempts to parse and solve basic algebraic equations."""
        try:
            # Try to extract equation patterns
            import re
            
            # Try pattern: "Solve for x: x + 9 = 34"
            solve_pattern = r'[Ss]olve\s+for\s+x\s*:\s*x\s*\+\s*(\d+)\s*=\s*(\d+)'
            matches = re.search(solve_pattern, question_content, re.IGNORECASE)
            
            if matches:
                # Extract the values
                constant = int(matches.group(1))
                result = int(matches.group(2))
                
                # Calculate x
                x_value = result - constant
                
                # Generate solution steps
                steps = [
                    f"Start with the original equation: x + {constant} = {result}",
                    f"To isolate x, subtract {constant} from both sides of the equation",
                    f"x + {constant} - {constant} = {result} - {constant}",
                    f"x = {result} - {constant} = {x_value}",
                    f"Therefore, x = {x_value}"
                ]
                
                return {
                    "content": f"The solution to the equation x + {constant} = {result} is x = {x_value}.",
                    "steps": "\n".join([f"Step {i+1}: {step}" for i, step in enumerate(steps)])
                }
            
            # Try general pattern: "x + 9 = 34"
            simple_addition = r'x\s*\+\s*(\d+)\s*=\s*(\d+)'
            matches = re.search(simple_addition, question_content)
            if matches:
                constant = int(matches.group(1))
                result = int(matches.group(2))
                x_value = result - constant
                
                steps = [
                    f"Start with the equation: x + {constant} = {result}",
                    f"Subtract {constant} from both sides: x = {result} - {constant}",
                    f"Solve for x: x = {x_value}"
                ]
                
                return {
                    "content": f"The solution is x = {x_value}.",
                    "steps": "\n".join([f"Step {i+1}: {step}" for i, step in enumerate(steps)])
                }
                
            # Try pattern for x - constant = result
            subtraction_pattern = r'x\s*-\s*(\d+)\s*=\s*(\d+)'
            matches = re.search(subtraction_pattern, question_content)
            if matches:
                constant = int(matches.group(1))
                result = int(matches.group(2))
                x_value = result + constant
                
                steps = [
                    f"Start with the equation: x - {constant} = {result}",
                    f"Add {constant} to both sides: x = {result} + {constant}",
                    f"Solve for x: x = {x_value}"
                ]
                
                return {
                    "content": f"The solution is x = {x_value}.",
                    "steps": "\n".join([f"Step {i+1}: {step}" for i, step in enumerate(steps)])
                }
                
            # Try pattern for constant * x = result
            multiplication_pattern = r'(\d+)\s*\*?\s*x\s*=\s*(\d+)'
            matches = re.search(multiplication_pattern, question_content)
            if matches:
                constant = int(matches.group(1))
                result = int(matches.group(2))
                x_value = result / constant
                
                steps = [
                    f"Start with the equation: {constant}x = {result}",
                    f"Divide both sides by {constant}: x = {result} / {constant}",
                    f"Solve for x: x = {x_value}"
                ]
                
                return {
                    "content": f"The solution is x = {x_value}.",
                    "steps": "\n".join([f"Step {i+1}: {step}" for i, step in enumerate(steps)])
                }
                
            return None
            
        except Exception as e:
            print(f"Error in equation solver: {e}")
            return None
    
    def _get_solution_template(self, question_type: QuestionType) -> str:
        """Get a solution template for a specific question type."""
        if question_type == QuestionType.MATH:
            return "To solve this equation, we need to isolate the variable by performing inverse operations. We'll move all constants to the right side and simplify to find the value of the variable."
        elif question_type == QuestionType.PHYSICS:
            return "This physics problem involves {keyword1}, which can be solved using the principle of {keyword2}. By applying the relevant equations and solving for the unknown variable, we find the final answer."
        else:
            return "The solution to this problem involves understanding the concept of {keyword1} and applying it correctly. By analyzing the {keyword2} and considering its relationship with {keyword3}, we can derive the answer."
    
    def _get_step_templates(self, question_type: QuestionType) -> List[str]:
        """Get step templates for a specific question type."""
        if question_type == QuestionType.MATH:
            return [
                "Start with the given equation and identify what we're solving for.",
                "Rearrange the equation by performing the same operation on both sides to isolate the variable.",
                "Simplify the equation by combining like terms if necessary.",
                "Solve for the variable by performing the final calculation.",
                "Verify the solution by substituting back into the original equation."
            ]
        elif question_type == QuestionType.PHYSICS:
            return [
                "Identify the physical principles: This problem involves {keyword1}.",
                "Set up the relevant equations: Write down the equations that relate to {keyword2}.",
                "Solve for the unknown variable: Manipulate the equations to isolate the variable we're looking for.",
                "Calculate the final answer: Plug in the values and compute the result."
            ]
        else:
            return [
                "Understand the problem: This question is asking about {keyword1}.",
                "Identify the key concepts: The main ideas here are {keyword2} and {keyword3}.",
                "Apply the relevant principles: Use the theoretical framework to approach the problem.",
                "Derive the conclusion: Based on the analysis, we can determine the answer."
            ] 