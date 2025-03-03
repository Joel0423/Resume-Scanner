import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
#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
from difflib import SequenceMatcher
from flask import flash
import re
from datetime import datetime
from datetime import timedelta
from docx2pdf import convert
import fitz
import os

from .jobseeker_results_genai import get_recommendations

# Load Spacy NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize NLTK's stemmer
stemmer = PorterStemmer()

# Stopword list for filtering
stop_words = set(stopwords.words("english"))

# Extract text from a resume file (PDF or Word)
def convert_docx_to_pdf(docx_path, output_pdf_path):
    """Convert DOCX to PDF using docx2pdf."""
    try:
        # Use docx2pdf to convert DOCX to PDF
        convert(docx_path, output_pdf_path)
        return output_pdf_path
    except Exception as e:
        raise RuntimeError(f"Failed to convert DOCX to PDF: {e}")

def extract_resume_text(file_path):
    num_pages = 0  # Variable to store the number of pages

    if file_path.endswith(".pdf"):
        # Use PyMuPDF to handle PDFs
        pdf_document = fitz.open(file_path)
        num_pages = pdf_document.page_count
        resume_text = " ".join([page.get_text() for page in pdf_document])
        pdf_document.close()
    elif file_path.endswith(".docx"):
        # Convert DOCX to PDF and process it
        temp_pdf_path = file_path.replace(".docx", ".pdf")
        pdf_path = convert_docx_to_pdf(file_path, temp_pdf_path)

        # Use PyMuPDF to extract text and page count from the converted PDF
        pdf_document = fitz.open(pdf_path)
        num_pages = pdf_document.page_count
        resume_text = " ".join([page.get_text() for page in pdf_document])
        pdf_document.close()

        # Clean up temporary PDF file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are allowed.")

    return resume_text, num_pages

# Preprocess text for JD
def preprocess_text_JD(text):
    filtered_tokens = [token.text for token in text if token.is_alpha and token.text not in stop_words]
    return " ".join(filtered_tokens)

# Job Description Scoring
def score_job_description(resume_text, job_description):
    resume_processed = preprocess_text_JD(resume_text)
    job_description = nlp(job_description.lower())
    job_processed = preprocess_text_JD(job_description)

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_processed, job_processed])
    similarity = cosine_similarity(vectors[0], vectors[1])

    return similarity[0][0] * 100

# Skills Scoring
def score_skills(resume_doc, skills):
    """
    Score skills by matching stemmed skills in the resume to those listed in the job description.
    """

    resume_skills = {
        stemmer.stem(token.text)
        for token in resume_doc
        if token.is_alpha and not token.is_stop  # Only include alphabetic, non-stopword tokens
    }

    # Preprocess skills from job description (scoring_weights.skills)
    job_skills = {stemmer.stem(skill.lower()) for skill in skills}

    # Find matches
    matched_skills = resume_skills.intersection(job_skills)

    # Calculate score
    score = 0
    max_weight = sum(skills.values())

    for skill, weight in skills.items():
        if stemmer.stem(skill.lower()) in matched_skills:
            score += weight

    return (score / max_weight) * 100 

# Education Scoring
def calculate_similarity(str1, str2):
    """Calculate a similarity score between two strings."""
    return SequenceMatcher(None, str1, str2).ratio()

def generate_ngrams(tokens, n):
    """Generate n-grams from a list of tokens."""
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]

def score_education(resume_text, specific_degrees, fallback_degrees):
    resume_text = resume_text.lower()
    matched_score = 0
    total_weight = sum(specific_degrees.values())

    # Tokenize resume text using SpaCy
    resume_doc = nlp(resume_text)
    resume_tokens = [token.text for token in resume_doc if token.is_alpha]

    # Generate n-grams from resume tokens (up to trigrams for flexibility)
    n_grams = []
    for n in range(1, 4):  # Generate unigrams, bigrams, and trigrams
        n_grams.extend(generate_ngrams(resume_tokens, n))

    def match_degree(degree, n_grams, threshold):
        """Match a degree against n-grams with a given similarity threshold."""
        for n_gram in n_grams:
            similarity = calculate_similarity(degree, n_gram)
            if similarity > threshold:
                return True
        return False

    # Match specific degrees
    for degree, weight in specific_degrees.items():
        degree_lower = degree.lower()
        if len(degree_lower.split()) == 1:  # Single-word degree
            if match_degree(degree_lower, n_grams, 0.6):  # Lower threshold for single words
                matched_score += weight
        else:  # Multi-word degree
            if match_degree(degree_lower, n_grams, 0.8):  # Higher threshold for multi-word
                matched_score += weight

    # Fallback scoring
    if matched_score == 0:
        total_weight = sum(fallback_degrees.values())
        for fallback, weight in fallback_degrees.items():
            fallback_lower = fallback.lower()
            if len(fallback_lower.split()) == 1:  # Single-word fallback degree
                if match_degree(fallback_lower, n_grams, 0.6):  # Lower threshold for single words
                    matched_score += weight
            else:  # Multi-word fallback degree
                if match_degree(fallback_lower, n_grams, 0.8):  # Higher threshold for multi-word
                    matched_score += weight

    return (matched_score / total_weight) * 100 if total_weight > 0 else 0 

# Places Worked Scoring
def score_places_worked(resume_text, preferred_companies, fallback_industry):
    resume_text = resume_text.lower()
    matched_score = 0
    total_weight = sum(preferred_companies.values())

    # Tokenize resume text using SpaCy
    resume_doc = nlp(resume_text)
    resume_tokens = [token.text for token in resume_doc if token.is_alpha]

    # Generate n-grams from resume tokens (up to trigrams for flexibility)
    n_grams = []
    for n in range(1, 4):  # Generate unigrams, bigrams, and trigrams
        n_grams.extend(generate_ngrams(resume_tokens, n))

    def match_company(company, n_grams, threshold):
        """Match a company against n-grams with a given similarity threshold."""
        for n_gram in n_grams:
            similarity = calculate_similarity(company, n_gram)
            if similarity > threshold:

                return True
        return False

    # Match preferred companies
    for company, weight in preferred_companies.items():
        company_lower = company.lower()
        if len(company_lower.split()) == 1:  # Single-word company
            if match_company(company_lower, resume_tokens, 0.8):  # Lower threshold for single words
                matched_score += weight
        else:  # Multi-word company
            if match_company(company_lower, n_grams, 0.8):  # Higher threshold for multi-word
                matched_score += weight

    return (matched_score / total_weight) * 100 if total_weight > 0 else 0  # Scale to max 12.5%

# Extract work experience section
def extract_work_experience_section(text):
    text = text.lower()
    tokens = [token.text for token in nlp(text) if token.is_alpha or token.is_digit]

    # Predefined keywords for work experience
    keywords = {"work experience", "experience", "employment history", "internship", "professional experience"}

    # Generate n-grams from tokens
    for n in range(1, 4):  # Unigrams, bigrams, trigrams
        ngrams = generate_ngrams(tokens, n)
        for idx, ngram in enumerate(ngrams):
            for keyword in keywords:
                if calculate_similarity(ngram, keyword) > 0.8:  # Similarity threshold
                    # Extract text from the first match of a keyword to the end of the resume
                    return " ".join(tokens[idx:])
    return ""  # Return empty string if no section found

# Extract dates
def extract_dates(text):
    text = text.lower()
    dates = []  # Use a list to preserve order

    # Define date patterns
    date_patterns = [
        r"\b\d{4}\b",  # Match 4-digit year (e.g., 2023)
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b",  # Abbreviated or full month YYYY (e.g., Apr 2023, April 2023)
        r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b",  # Full month names YYYY (e.g., January 2023)
        r"\b\d{1,2}\/\d{4}\b",  # MM/YYYY or M/YYYY (e.g., 4/2023, 04/2023)
    ]

    # Match and add dates
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if match.strip() not in dates:  # Ensure no duplicates while preserving order
                dates.append(match.strip())

    return dates



# Normalize dates
def normalize_dates(dates):
    normalized_dates = []

    for date in dates:
        try:
            # Handle different date formats
            date = date.lower().strip()  # Normalize casing and strip whitespace
            
            if re.match(r"\b\d{4}\b", date):  # YYYY
                normalized_dates.append(datetime.strptime(date, "%Y"))
            elif re.match(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b \d{4}", date):  # Month YYYY
                normalized_dates.append(datetime.strptime(date, "%b %Y"))
            elif re.match(r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b \d{4}", date):  # Full month name YYYY
                normalized_dates.append(datetime.strptime(date, "%B %Y"))
            elif re.match(r"\b\d{1,2}\/\d{4}\b", date):  # MM/YYYY
                normalized_dates.append(datetime.strptime(date, "%m/%Y"))
        except ValueError:
            continue  # Skip invalid dates

    return normalized_dates

# Calculate years worked
def calculate_years_worked(dates):
    if len(dates) < 2:
        return 0  # Not enough dates to calculate duration

    # Find earliest and latest dates
    earliest = min(dates)
    latest = max(dates)

    # Calculate the difference in years
    years_worked = (latest - earliest).days / 365.25
    return round(years_worked, 2)

# Main function to score years worked
def score_years_worked(resume_text, scoring_weights):
    # Extract work experience section
    work_experience_section = extract_work_experience_section(resume_text)

    if not work_experience_section:
        return 0  # No work experience section found

    # Extract and normalize dates
    dates = extract_dates(work_experience_section)

    normalized_dates = normalize_dates(dates)


    # Calculate years worked
    years_worked = calculate_years_worked(normalized_dates)

    if(years_worked>= scoring_weights.min_years and years_worked< scoring_weights.preferred_years):
        return (scoring_weights.min_years_weight/5 )* 100
    elif(years_worked >= scoring_weights.preferred_years):
        return 100
    return 0

def extract_dates_gap(text):
    text = text.lower()
    dates = []  # Use a list to preserve order

    # Define date patterns
    date_patterns = [
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b",  # Abbreviated or full month YYYY (e.g., Apr 2023, April 2023)
        r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b",  # Full month names YYYY (e.g., January 2023)
        r"\b\d{1,2}\/\d{4}\b",  # MM/YYYY or M/YYYY (e.g., 4/2023, 04/2023)
        r"\b\d{4}\b",  # Match 4-digit year (e.g., 2023) last to ensure specific dates are matched first
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            match = match.strip()
            
            # Skip standalone years already part of a more specific date
            if re.match(r"^\d{4}$", match):  # If match is a standalone year
                if any(match in date for date in dates):  # Skip if already part of an existing date
                    continue
            
            if match not in dates:  # Ensure no duplicates
                dates.append(match)

    return dates



# Normalize dates
def normalize_dates_gap(dates):
    normalized_dates = []

    for date in dates:
        try:
            # Handle different date formats
            date = date.lower().strip()  # Normalize casing and strip whitespace
            
            if re.match(r"\b\d{4}\b", date):  # YYYY
                normalized_dates.append(datetime.strptime(date, "%Y"))
            elif re.match(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b \d{4}", date):  # Month YYYY
                normalized_dates.append(datetime.strptime(date, "%b %Y"))
            elif re.match(r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b \d{4}", date):  # Full month name YYYY
                normalized_dates.append(datetime.strptime(date, "%B %Y"))
            elif re.match(r"\b\d{1,2}\/\d{4}\b", date):  # MM/YYYY
                normalized_dates.append(datetime.strptime(date, "%m/%Y"))
        except ValueError:
            continue  # Skip invalid dates

    return normalized_dates


# Gaps Scoring
def score_gaps(resume_text, max_gap_tolerance, gap_negative_weight, scoring_weights):
    # Extract work experience section

    work_experience_section = extract_work_experience_section(resume_text)

    if not work_experience_section:
        return 0  # No work experience section found

    # Extract and normalize dates
    dates = extract_dates_gap(work_experience_section)

    normalized_dates = normalize_dates_gap(dates)

    if not normalized_dates:
        return 0  # No dates found in the work experience section
    

    # Find the maximum gap between consecutive years
    max_gap = timedelta(days=0)
    for i in range(2, len(normalized_dates),2):
        
        gap = normalized_dates[i] - normalized_dates[i - 1]

        if gap > max_gap:
            max_gap = gap

    # Determine the score based on the maximum gap
    if max_gap > timedelta(days=max_gap_tolerance * 365):
        return (gap_negative_weight/5)*100  # Apply penalty
    return 100  # Full score if no significant gap

# No. pages
def score_pages(num, ranges):

    for page_range, weight in ranges.items():
        start, end = map(int, page_range.split('-'))  # Convert range to integers

        if start <= num <= end:
            return (weight/5) *100 # Return the weight if the page is within the range
    return 0.0  # Return 0 if no match is found


# Bullets vs Paragraphs Scoring
def score_bullets_vs_paragraphs(resume_text, bullet_weight, paragraph_weight):
    doc = nlp(resume_text)

    # Split the resume into paragraphs by double line breaks (new paragraph)
    paragraphs = resume_text.split('\n\n')

    # Count paragraphs (excluding empty ones)
    paragraph_count = len([p for p in paragraphs if len(p.strip()) > 0])

    # Enhanced Bullet Point Detection
    # Regex to match different bullet styles
    bullet_pattern = re.compile(r"^\s*[-*•▪+]|\d+[\.\)]", re.MULTILINE)  # Handles '-', '*', '•', '1.', '1)', etc.
    bullet_points = re.findall(bullet_pattern, resume_text)
    
    # Use spaCy's tokenization to detect more features (optional)
    bullet_noun_phrases = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 5]  # Small noun phrases likely to be bullets

    paragraph_sentences = [sent.text for sent in doc.sents if len(sent.text.split()) > 15]  # Sentences with more than 15 words are considered paragraphs
    print("here")
    
    b = len(bullet_noun_phrases) + len(bullet_points)

    p = paragraph_count + len(paragraph_sentences)

    if(b>p):
        return (bullet_weight/5)*100
    else:
        return (paragraph_weight/5)*100


# Main Scoring Function
def calculate_resume_results(file_path, job_description, scoring_weights):
    resume_text, num_pages = extract_resume_text(file_path)
    print(resume_text)
    print(num_pages)

    resume_doc = nlp(resume_text.lower())

    scores = {}
    scores["job_description"] = score_job_description(resume_doc, job_description)
    print("1")
    scores["skills"] = score_skills(resume_doc, scoring_weights.skills)
    print("2")
    scores["education"] = score_education(resume_text, scoring_weights.specific_degrees, scoring_weights.fallback_degrees)
    print("3")
    scores["places_worked"] = score_places_worked(resume_text, scoring_weights.preferred_companies, scoring_weights.fallback_industry)
    print("4")
    scores["gaps"] = score_gaps(resume_text, scoring_weights.max_gap_tolerance, scoring_weights.gap_negative_weight, scoring_weights)
    print("5")
    scores["bullets_vs_paragraphs"] = score_bullets_vs_paragraphs(
        resume_text,
        scoring_weights.bullet_weight,
        scoring_weights.paragraph_weight
    )
    print("6")
    scores["years_worked"] = score_years_worked(resume_text, scoring_weights)
    print("7")
    scores["pages"] = score_pages(num_pages, scoring_weights.page_ranges)
    print("8")

    total_score = sum(scores.values())/8  # Total out of 100%
    
    # Flash results for display
    flash({"total_score": total_score, "section_scores": scores}, category="scores")

    gemini_recomm = get_recommendations(scores, resume_doc, job_description)
    flash(gemini_recomm, category="jobseek_recommendations")

    return {"total_score": total_score, "section_scores": scores, "recommendations": gemini_recomm}