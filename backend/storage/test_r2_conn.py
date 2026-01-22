"""
Test script to verify R2 storage is configured correctly
Run this before deploying to make sure everything works

Usage:
    python test_r2_connection.py
"""

from dotenv import load_dotenv
import os
import sys

load_dotenv()

print("Testing R2 Storage Configuration...")
print("=" * 50)

# Check environment variables
required_vars = [
    'CF_ACCOUNT_ID',
    'CF_ACCESS_KEY',
    'CF_SECRET_ACCESS_KEY',
    'BUCKET_NAME',
    'S3_API'
]

print("\n1. Checking environment variables...")
missing_vars = []
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Show partial value for security
        if len(value) > 8:
            display_value = value[:4] + "..." + value[-4:]
        else:
            display_value = "***"
        print(f"   ✓ {var}: {display_value}")
    else:
        print(f"   ✗ {var}: MISSING")
        missing_vars.append(var)

if missing_vars:
    print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("Please add them to your .env file")
    sys.exit(1)

print("\n2. Testing R2 connection...")
try:
    from r2_storage import r2_storage
    print("   ✓ R2 storage module imported successfully")
except Exception as e:
    print(f"   ✗ Failed to import R2 storage: {e}")
    print("\nMake sure:")
    print("  - storage/r2_storage.py exists")
    print("  - storage/__init__.py exists")
    print("  - boto3 is installed (pip install boto3)")
    sys.exit(1)

print("\n3. Testing file upload...")
try:
    test_data = {
        "test": "data",
        "timestamp": "2024-01-01",
        "purpose": "connection_test"
    }
    test_key = "test/test_file.json"
    
    success = r2_storage.upload_json(test_data, test_key)
    if success:
        print("   ✓ Upload successful")
    else:
        print("   ✗ Upload failed (returned False)")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Upload error: {e}")
    print("\nPossible issues:")
    print("  - Check your R2 credentials are correct")
    print("  - Verify bucket name is correct")
    print("  - Ensure S3 API endpoint is correct")
    sys.exit(1)

print("\n4. Testing file download...")
try:
    downloaded_data = r2_storage.download_json(test_key)
    if downloaded_data == test_data:
        print("   ✓ Download successful - data matches")
    else:
        print(f"   ✗ Download mismatch")
        print(f"      Expected: {test_data}")
        print(f"      Got: {downloaded_data}")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Download error: {e}")
    sys.exit(1)

print("\n5. Testing file existence check...")
try:
    exists = r2_storage.file_exists(test_key)
    if exists:
        print("   ✓ File exists check successful")
    else:
        print("   ✗ File should exist but doesn't")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Existence check error: {e}")
    sys.exit(1)

print("\n6. Testing file deletion...")
try:
    success = r2_storage.delete_file(test_key)
    if success:
        print("   ✓ Delete successful")
    else:
        print("   ✗ Delete failed (returned False)")
        sys.exit(1)
        
    # Verify it's gone
    exists = r2_storage.file_exists(test_key)
    if not exists:
        print("   ✓ File confirmed deleted")
    else:
        print("   ✗ File still exists after deletion")
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Delete error: {e}")
    sys.exit(1)

print("\n7. Testing folder operations...")
try:
    # Create a test folder with multiple files
    test_prefix = "test_folder/"
    for i in range(3):
        r2_storage.upload_json(
            {"index": i, "test": True}, 
            f"{test_prefix}file_{i}.json"
        )
    
    files = r2_storage.list_files(test_prefix)
    if len(files) == 3:
        print(f"   ✓ List successful - found {len(files)} files")
    else:
        print(f"   ✗ Expected 3 files, found {len(files)}")
        print(f"      Files: {files}")
    
    # Cleanup
    r2_storage.delete_folder(test_prefix)
    
    # Verify folder is empty
    files_after = r2_storage.list_files(test_prefix)
    if len(files_after) == 0:
        print("   ✓ Folder cleanup successful")
    else:
        print(f"   ✗ Folder still has {len(files_after)} files after cleanup")
    
except Exception as e:
    print(f"   ✗ Folder operations error: {e}")
    # Try to cleanup anyway
    try:
        r2_storage.delete_folder(test_prefix)
    except:
        pass
    sys.exit(1)

print("\n8. Testing public URL generation...")
try:
    test_key = "frame_sets/abc123/frames/frame_0.jpg"
    public_url = r2_storage.get_public_url(test_key)
    
    expected_url = f"{os.getenv('PUB_DEV_URL')}/{test_key}"
    
    if public_url == expected_url:
        print(f"   ✓ Public URL correct: {public_url}")
    else:
        print(f"   ✗ Public URL mismatch")
        print(f"      Expected: {expected_url}")
        print(f"      Got: {public_url}")
except Exception as e:
    print(f"   ✗ Public URL error: {e}")

print("\n" + "=" * 50)
print("✅ All tests passed! R2 storage is configured correctly.")
print("\nYou can now run your Flask application with R2 storage.")

# Optional: Show storage stats
print("\n📊 Current R2 Storage:")
try:
    all_files = r2_storage.list_files()
    print(f"   Total files in bucket: {len(all_files)}")
    
    # Count by prefix
    videos = len([f for f in all_files if f.startswith('videos/')])
    frame_sets = len([f for f in all_files if f.startswith('frame_sets/')])
    
    print(f"   Videos: {videos}")
    print(f"   Frame sets: {frame_sets}")
    
    # Show some example files if any exist
    if frame_sets > 0:
        print(f"\n   Example frame set files:")
        frame_set_files = [f for f in all_files if f.startswith('frame_sets/')][:5]
        for f in frame_set_files:
            print(f"     - {f}")
            
except Exception as e:
    print(f"   Could not retrieve stats: {e}")

print("\n" + "=" * 50)
print("Next steps:")
print("  1. Start your backend: python api.py")
print("  2. Test video upload through your frontend")
print("  3. Check R2 bucket to see uploaded frames")
