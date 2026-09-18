Yes. The safest approach is:

## On This Laptop

Copy the project folder to a USB drive or company storage, but exclude:

- `.venv`
- `.env`
- `db.sqlite3`
- `__pycache__/`
- `.git` if you do not need the existing Git history

Keep:

- `apps`
- `config`
- `manage.py`
- `requirements.txt`
- `README.md`
- migrations
- Postman collection files

Do not upload your API keys. Create a new `.env` on the company laptop.

## On the Company Laptop

After copying the project:

```powershell
cd path\to\ai_prompt_manager

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create `.env`:

```env
SECRET_KEY=your-new-django-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

ANTHROPIC_MODEL=claude-3-5-haiku-latest
ANTHROPIC_MAX_TOKENS=1024
DEFAULT_AI_PROVIDER=openai
```

Then run:

```powershell
python manage.py migrate
python manage.py check
python manage.py test
python manage.py runserver
```

## Upload from Company Laptop

If you want to upload it to GitHub there:

```powershell
git init
git add .
git commit -m "feat: complete AI prompt manager backend"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Before running `git add .`, verify:

```powershell
git status
```

Make sure `.env`, `.venv`, and `db.sqlite3` are not listed.

Because the OpenAI key appeared in an earlier Git diff, rotate that key before continuing. Use a new key in the company laptop’s `.env`.



# AI Prompt Manager

AI Prompt Manager is a Django REST Framework backend for creating, organizing, versioning, and improving AI prompts. Users can keep prompts private, publish prompts for other users, and request generated or improved prompts from supported AI providers.

## Features

- Email-based user registration and token authentication
- Prompt and category CRUD APIs
- Public and private prompts
- Owner-only write access
- Public prompt visibility for other authenticated users
- Prompt version history
- AI prompt improvement and generation
- OpenAI and Anthropic provider implementations
- AI execution logging with token usage
- Pagination and prompt search/filter support through DRF configuration

## Local Setup

Requirements:

- Python 3.11 or newer
- An OpenAI API key and/or Anthropic API key for AI endpoints

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=replace-with-openai-key
ANTHROPIC_API_KEY=replace-with-anthropic-key
ANTHROPIC_MODEL=claude-3-5-haiku-latest
ANTHROPIC_MAX_TOKENS=1024
DEFAULT_AI_PROVIDER=openai
```

Apply migrations and start the development server:

```powershell
python manage.py migrate
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/`.

## API Endpoints

All endpoints except registration and login require:

```http
Authorization: Token <token>
```

### Authentication

- `POST /api/v1/auth/register/` - create a user with `email`, `username`, and `password`
- `POST /api/v1/auth/login/` - authenticate with `email` and `password`
- `POST /api/v1/auth/logout/` - revoke the current user's token

### Prompts and Categories

- `GET|POST /api/v1/categories/`
- `GET|PUT|PATCH|DELETE /api/v1/categories/{id}/`
- `GET|POST /api/v1/prompts/`
- `GET|PUT|PATCH|DELETE /api/v1/prompts/{id}/`
- `GET /api/v1/prompts/{id}/history/`

A prompt owner can read and modify their own prompts. Other authenticated users can read public prompts only.

### AI Operations

- `POST /api/v1/ai/improve/`
- `POST /api/v1/ai/generate/`
- `GET /api/v1/ai/usage/` - view the authenticated user's AI usage statistics

Example improve request:

```json
{
  "prompt_content": "Write a product announcement.",
  "instructions": "Make it concise and professional.",
  "provider": "openai"
}
```

Example generate request:

```json
{
  "description": "Create a prompt that summarizes customer feedback.",
  "provider": "anthropic"
}
```

AI requests return the generated result and provider metadata. Each attempt is recorded in `AIExecutionLog`, including provider, action, input, output when successful, and token usage.

The usage endpoint returns total requests, improve and generate counts, total tokens, failed requests, and a breakdown grouped by provider.

## Testing

Run Django checks and the test suite with:

```powershell
python manage.py check
python manage.py test
```

## Architecture

The project is split into three Django apps:

- `users` contains the custom user model, registration, login, logout, and serializers.
- `prompts` contains categories, prompts, prompt history, permissions, serializers, and prompt business services.
- `ai_service` contains AI request serializers, API views, execution logging, and provider implementations.

Prompt creation and version updates are handled by `PromptService` inside database transactions. API views validate request data through DRF serializers, while object permissions enforce private/public prompt access.

## AI Provider Abstraction

Every provider implements `BaseAIProvider` with these operations:

- `improve_prompt(prompt_content, instructions="")`
- `generate_prompt(description)`

`AIProviderFactory` selects the implementation by provider name. Current providers are `openai` and `anthropic`. API views depend on the factory and base interface rather than provider-specific SDKs.

To add another provider:

1. Add its SDK to `requirements.txt`.
2. Create a class in `apps/ai_service/providers/` that implements `BaseAIProvider`.
3. Read the provider API key and model from environment variables.
4. Return the generated text and normalized metadata containing token counts where available.
5. Register the class in `AIProviderFactory._providers`.
6. Add tests for success, invalid provider selection, missing credentials, and upstream failures.

Provider failures are logged server-side and returned to clients as a generic `502 Bad Gateway` response. Unsupported provider names return `400 Bad Request`.
