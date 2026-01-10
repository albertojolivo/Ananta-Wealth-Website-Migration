require 'open-uri'
require 'fileutils'
require 'uri'

# Configuration
BASE_URL = "https://www.anantawealth.com"
INPUT_FILE = "original_index.html"
OUTPUT_FILE = "index.html"
ASSET_DIRS = {
  "css" => "css",
  "js" => "js",
  "image" => "images",
  "font" => "fonts"
}

# Create directories
ASSET_DIRS.values.each do |dir|
  FileUtils.mkdir_p(dir)
end

def download_file(url, folder, default_ext="")
  begin
    # Handle protocol-relative URLs
    if url.start_with?("//")
      url = "https:" + url
    end

    # Absolute URL
    full_url = URI.join(BASE_URL, url).to_s
    
    # Parse filename
    parsed = URI.parse(full_url)
    filename = File.basename(parsed.path)
    
    # Handle missing filename
    if filename.nil? || filename.empty? || filename == "/"
      return url
    end

    # Clean filename
    filename = filename.gsub(/[<>:"\/\\|?*]/, '_')
    
    if File.extname(filename).empty? && !default_ext.empty?
      filename += default_ext
    end

    local_path = File.join(folder, filename)
    
    # Check if exists
    if File.exist?(local_path)
      # puts "Skipping existing: #{filename}"
      return "#{folder}/#{filename}"
    end

    puts "Downloading: #{full_url} -> #{local_path}"
    
    # Download
    URI.open(full_url, "User-Agent" => "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)") do |image|
      File.open(local_path, "wb") do |file|
        file.write(image.read)
      end
    end
    
    return "#{folder}/#{filename}"
  rescue => e
    puts "Failed to download #{url}: #{e.message}"
    return url
  end
end

content = File.read(INPUT_FILE)

# 1. CSS Links
content = content.gsub(/<link[^>]+href=["']([^"']+)["'][^>]*>/) do |match|
  full_tag = match
  href = $1
  
  if full_tag.include?('rel="stylesheet"') || full_tag.include?("rel='stylesheet'") || href.end_with?('.css')
     new_path = download_file(href, ASSET_DIRS["css"], ".css")
     full_tag.sub(href, new_path)
  else
    full_tag
  end
end

# 2. Scripts
content = content.gsub(/<script[^>]+src=["']([^"']+)["'][^>]*>/) do |match|
  full_tag = match
  src = $1
  new_path = download_file(src, ASSET_DIRS["js"], ".js")
  full_tag.sub(src, new_path)
end

# 3. Images
content = content.gsub(/<img[^>]+src=["']([^"']+)["'][^>]*>/) do |match|
  full_tag = match
  src = $1
  
  # Remove srcset
  full_tag = full_tag.gsub(/srcset=["'][^"']+["']/, '')
  
  unless src.start_with?("data:")
    new_path = download_file(src, ASSET_DIRS["image"])
    full_tag.sub(src, new_path)
  else
    full_tag
  end
end

File.write(OUTPUT_FILE, content)
puts "Done! Saved to #{OUTPUT_FILE}"
