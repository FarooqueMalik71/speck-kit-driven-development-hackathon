# Data Model: AI-Native Textbook Platform

## Content Entities

### TextbookContent
- **id**: UUID (primary key)
- **title**: string
- **content_type**: enum (text, code, figure, simulation, video, interactive)
- **content**: text (markdown or HTML)
- **difficulty_level**: enum (beginner, intermediate, advanced)
- **prerequisites**: JSON array of content IDs
- **learning_objectives**: JSON array of strings
- **tags**: JSON array of strings (ROS2, embodied-ai, etc.)
- **parent_id**: UUID (foreign key to parent content)
- **content_path**: string (hierarchical path)
- **created_at**: timestamp
- **updated_at**: timestamp
- **version**: integer

### ContentMetadata
- **content_id**: UUID (foreign key to TextbookContent)
- **word_count**: integer
- **reading_time**: integer (in minutes)
- **related_content**: JSON array of content IDs
- **cross_references**: JSON array of content IDs
- **vector_embedding_id**: string (reference to Qdrant)

## User Entities

### User
- **id**: UUID (primary key)
- **email**: string (unique)
- **username**: string (unique, optional)
- **auth_provider**: string (google, github, institutional)
- **auth_provider_id**: string
- **role**: enum (student, faculty, admin)
- **preferences**: JSON object
- **created_at**: timestamp
- **updated_at**: timestamp
- **last_login_at**: timestamp

### UserProfile
- **user_id**: UUID (foreign key to User)
- **display_name**: string
- **learning_style**: enum (visual, textual, interactive)
- **language_preference**: string (ISO 639-1)
- **timezone**: string (IANA)
- **institution**: string (optional)
- **program**: string (optional)
- **year**: integer (optional)

## Learning & Interaction Entities

### UserProgress
- **id**: UUID (primary key)
- **user_id**: UUID (foreign key to User)
- **content_id**: UUID (foreign key to TextbookContent)
- **status**: enum (not_started, in_progress, completed)
- **completion_percentage**: float (0-100)
- **time_spent**: integer (in seconds)
- **last_accessed_at**: timestamp
- **progress_data**: JSON object (for interactive elements)

### UserNotes
- **id**: UUID (primary key)
- **user_id**: UUID (foreign key to User)
- **content_id**: UUID (foreign key to TextbookContent)
- **note_text**: text
- **note_type**: enum (bookmark, highlight, personal_note)
- **selection_start**: integer (character offset)
- **selection_end**: integer (character offset)
- **created_at**: timestamp
- **updated_at**: timestamp

### UserQuestions
- **id**: UUID (primary key)
- **user_id**: UUID (foreign key to User)
- **content_id**: UUID (foreign key to TextbookContent, nullable for full-book Q&A)
- **question_text**: text
- **answer_text**: text
- **answer_source**: JSON array of content references
- **confidence_score**: float (0-1)
- **is_full_book_qa**: boolean
- **created_at**: timestamp
- **feedback_rating**: integer (-1 to 1, for response quality)

## AI & Personalization Entities

### PersonalizationProfile
- **user_id**: UUID (foreign key to User)
- **learning_preferences**: JSON object
- **difficulty_adaptation**: float (0-1, adjusts content difficulty)
- **recommended_content**: JSON array of content IDs
- **learning_path**: JSON array of content IDs
- **performance_metrics**: JSON object
- **updated_at**: timestamp

### AIInteractionLog
- **id**: UUID (primary key)
- **user_id**: UUID (foreign key to User, nullable for anonymous)
- **session_id**: string
- **query_text**: text
- **response_text**: text
- **response_metadata**: JSON object (confidence, sources, tokens used)
- **interaction_type**: enum (full_book_qa, selected_text_qa, translation, personalization)
- **created_at**: timestamp
- **response_time_ms**: integer

## Translation Entities

### TranslationCache
- **id**: UUID (primary key)
- **content_id**: UUID (foreign key to TextbookContent)
- **source_language**: string (ISO 639-1)
- **target_language**: string (ISO 639-1)
- **translated_content**: text
- **translation_metadata**: JSON object
- **expires_at**: timestamp
- **created_at**: timestamp

## System Entities

### SystemConfiguration
- **key**: string (primary key)
- **value**: JSON
- **description**: string
- **updated_at**: timestamp

## Validation Rules

### TextbookContent
- Title must be 1-200 characters
- Content type must be valid enum value
- Difficulty level must be valid enum value
- Content path must follow hierarchical format
- Version must be incremented on updates

### User
- Email must be valid format
- Role must be valid enum value
- Auth provider and provider ID must match

### UserProgress
- Status must be valid enum value
- Completion percentage must be 0-100
- User and content must exist

### UserQuestions
- Question text must be 1-2000 characters
- Confidence score must be 0-1
- Feedback rating must be -1, 0, or 1

## State Transitions

### UserProgress Status Transitions
- not_started → in_progress (when user starts content)
- in_progress → completed (when user finishes content)
- completed → in_progress (when user revisits content)

## Relationships

### Content Hierarchy
- TextbookContent (parent_id) → TextbookContent (id) [self-referencing]

### User Content Relationships
- User → UserProgress [one-to-many]
- TextbookContent → UserProgress [one-to-many]
- User → UserNotes [one-to-many]
- TextbookContent → UserNotes [one-to-many]

### AI Interaction Relationships
- User → UserQuestions [one-to-many]
- TextbookContent → UserQuestions [one-to-many, nullable]
- User → AIInteractionLog [one-to-many, nullable]