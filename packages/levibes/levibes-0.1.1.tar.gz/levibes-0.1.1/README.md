<p align="center">
   <img src="https://github.com/user-attachments/assets/24d6a4c4-6313-4b89-99c2-3c15783d7eaa" alt="working demo" />
</p>
<h1 align="center"> LeVibes </h1>
<p align="center">Generate <bold>motivational</bold> social media posts with <bold>AI</bold> and <bold>LeBron James</bold>
<p align="center">
  <img alt="Stars" src="https://img.shields.io/github/stars/makors/levibes" />
  <img alt="Watchers" src="https://img.shields.io/github/watchers/makors/levibes" />
</p>

## Features

- Generate beautiful motivational images with AI-powered captions
- Upload images as draft slideshows to TikTok
- Cloudflare R2 integration for image hosting
- Interactive CLI interface

## Installation

```bash
# Clone the repository
git clone https://github.com/makors/levibes
cd levibes

# Install dependencies using uv
uv sync

# Or with pip
pip install -e .
```

## Configuration

Create a `.env` file in the project root with the following variables:

### Complete Example .env File

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# TikTok API Configuration
TIKTOK_CLIENT_ID=your_tiktok_client_id
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret

# Cloudflare R2 Configuration
CLOUDFLARE_R2_ENDPOINT_URL=https://abc123def456.r2.cloudflarestorage.com
CLOUDFLARE_R2_ACCESS_KEY_ID=your_r2_access_key_id
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
CLOUDFLARE_R2_BUCKET_NAME=my-levibes-bucket

# R2 Public URL (r2.dev subdomain - recommended)
CLOUDFLARE_R2_PUBLIC_URL_BASE=https://my-levibes-bucket.r2.dev
```

### Environment Variables Breakdown

#### OpenAI Configuration
```env
OPENAI_API_KEY=your_openai_api_key_here
```

#### TikTok API Configuration
```env
TIKTOK_CLIENT_ID=your_tiktok_client_id
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
```

#### Cloudflare R2 Configuration
```env
# Required R2 variables
CLOUDFLARE_R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
CLOUDFLARE_R2_ACCESS_KEY_ID=your_r2_access_key_id
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
CLOUDFLARE_R2_BUCKET_NAME=your_r2_bucket_name

# Optional: Public URL base for accessing files
# Use r2.dev subdomain: https://your-bucket-name.r2.dev
# Or custom domain: https://your-custom-domain.com
CLOUDFLARE_R2_PUBLIC_URL_BASE=https://your-bucket-name.r2.dev
```

### Setting up Cloudflare R2

1. **Create a Cloudflare R2 Bucket:**
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
   - Navigate to R2 Object Storage
   - Create a new bucket with a unique name
   - Note the bucket name for your `.env` file

2. **Create R2 API Token:**
   - Go to "Manage R2 API Tokens"
   - Create a new API token with read/write permissions
   - Note the Access Key ID and Secret Access Key

3. **Configure Public Access:**
   - In your bucket settings, enable public access
   - This will give you an r2.dev subdomain: `https://your-bucket-name.r2.dev`
   - Set `CLOUDFLARE_R2_PUBLIC_URL_BASE=https://your-bucket-name.r2.dev`
   - Alternatively, configure a custom domain if desired

> **💡 Using r2.dev Subdomain**
> 
> If you're using an r2.dev subdomain (like `https://my-bucket.r2.dev`), this is the **recommended and simplest approach**:
> 
> 1. Enable public access on your R2 bucket
> 2. Use the provided r2.dev URL as your `CLOUDFLARE_R2_PUBLIC_URL_BASE`
> 3. The app will upload via the R2 API and serve files via the r2.dev subdomain
> 
> **Example configuration:**
> ```env
> CLOUDFLARE_R2_PUBLIC_URL_BASE=https://my-levibes-bucket.r2.dev
> ```

4. **Set R2 Endpoint URL:**
   - Format: `https://your-account-id.r2.cloudflarestorage.com`
   - Replace `your-account-id` with your actual Cloudflare account ID
   - This is used for uploads via API, not for public access

### Setting up TikTok API

1. **Create TikTok Developer Account:**
   - Go to [TikTok for Developers](https://developers.tiktok.com)
   - Create a developer account
   - Create a new app

2. **Configure App Settings:**
   - Set redirect URI to: `https://tiktoklocal.com:8080/callback`
   - Enable the following scopes:
     - `user.info.basic`
     - `user.info.profile`
     - `video.upload`
   - Note the Client ID and Client Secret

3. **Domain Configuration:**
   - Add `tiktoklocal.com` to your hosts file pointing to `127.0.0.1`
   - On macOS/Linux: `echo "127.0.0.1 tiktoklocal.com" | sudo tee -a /etc/hosts`
   - On Windows: Add to `C:\Windows\System32\drivers\etc\hosts`

## Usage

### Basic Usage

```bash
# Run the application
python main.py

# Or use the CLI directly
levibes
```

### Command Line Options

```bash
# Generate images only
python main.py --no-upload

# Upload existing images
python main.py --upload-only

# Specify custom output directory
python main.py --output-dir ./my-images

# Set custom caption
python main.py --caption "Follow for more motivation!"
```

### TikTok Upload Process

1. **Authentication:**
   - The app will open a browser for TikTok OAuth
   - You may see a security warning (SSL certificate)
   - Click "Advanced" and "Proceed to tiktoklocal.com"
   - Authorize the app

2. **Image Upload:**
   - Images are first uploaded to Cloudflare R2
   - R2 URLs are then used to create TikTok draft
   - Draft appears in your TikTok app inbox

3. **Publishing:**
   - Open TikTok app on your phone
   - Go to inbox and find the draft
   - Edit and publish as desired

## File Structure

```
levibes/
├── src/levibes/
│   ├── caption_generation.py  # AI caption generation
│   ├── generate_images.py     # Image creation
│   ├── upload.py             # TikTok/R2 upload
│   ├── cli.py                # Command line interface
│   └── config.py             # Configuration management
├── output/                   # Generated images
├── main.py                   # Entry point
└── .env                      # Environment variables
```

## API Limits

- **TikTok API:** 6 requests per minute per user
- **R2 Storage:** Check your Cloudflare plan limits
- **OpenAI API:** Based on your plan and usage

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure all required variables are set in `.env`
   - Check for typos in variable names

2. **"Authorization failed"**
   - Verify TikTok Client ID and Secret
   - Check that redirect URI is correctly configured
   - Ensure `tiktoklocal.com` is in your hosts file

3. **"Failed to upload to R2"**
   - Verify R2 credentials and bucket name
   - Check bucket permissions
   - Ensure endpoint URL is correct
   - If using r2.dev subdomain, make sure public access is enabled on the bucket

4. **SSL Certificate Warning**
   - This is normal for local development
   - Click "Advanced" and "Proceed to tiktoklocal.com"

### Debug Mode

Set `DEBUG=1` in your `.env` file for detailed logging:

```env
DEBUG=1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.