import os
import sys
import importlib
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_dependencies():
    """Check if all required packages are installed."""
    print("\n📦 Checking dependencies...")
    required_packages = [
        'requests', 'bs4', 'pandas', 'numpy',
        'llama_index', 'chromadb', 'flask', 'supabase',
        'sentence_transformers', 'torch', 'transformers'
    ]
    
    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    return True

def check_project_structure():
    """Check if project structure is correct."""
    print("\n📁 Checking project structure...")
    
    required_dirs = [
        'data', 'data/raw', 'data/processed', 'data/logs',
        'scripts', 'src', 'src/backend', 'src/frontend', 
        'src/storage', 'utils', 'tests'
    ]
    
    required_files = [
        'requirements.txt', 'main.py', 'scripts/run_pipeline.py',
        'src/frontend/app.py', 'utils/constants.py'
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
        else:
            print(f"✅ {dir_path}/ - OK")
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} - OK")
    
    if missing_dirs or missing_files:
        print(f"\n⚠️  Missing directories: {missing_dirs}")
        print(f"⚠️  Missing files: {missing_files}")
        return False
    return True

def check_init_files():
    """Check if __init__.py files exist in packages."""
    print("\n📦 Checking package initialization...")
    
    init_locations = [
        'src/__init__.py', 'src/backend/__init__.py', 
        'src/frontend/__init__.py', 'src/storage/__init__.py',
        'src/ai/__init__.py', 'scripts/__init__.py',
        'utils/__init__.py', 'tests/__init__.py'
    ]
    
    missing = []
    for init_file in init_locations:
        if not os.path.exists(init_file):
            missing.append(init_file)
        else:
            print(f"✅ {init_file} - OK")
    
    if missing:
        print(f"\n⚠️  Missing __init__.py files: {missing}")
        return False
    return True

def check_environment_variables():
    """Check if required environment variables are set."""
    print("\n🔑 Checking environment variables...")
    
    required_vars = ['ANTHROPIC_API_KEY']
    optional_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_BUCKET']
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_required.append(var)
        else:
            print(f"✅ {var} - OK")
    
    for var in optional_vars:
        if not os.environ.get(var):
            missing_optional.append(var)
            print(f"⚠️  {var} - NOT SET (optional)")
        else:
            print(f"✅ {var} - OK")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {missing_required}")
        print("Create a .env file with these variables")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Optional variables not set: {missing_optional}")
        print("These are needed for Supabase integration")
    
    return True

def check_imports():
    """Check if key modules can be imported."""
    print("\n🔍 Checking imports...")
    
    # Add project root to path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    modules_to_test = [
        ('scripts.run_pipeline', 'run'),
        ('src.frontend.app', 'app'),
        ('utils.constants', 'BRANDS'),
        ('src.backend.generate_combo', 'generate_combo'),
        ('src.storage.leaderboard', 'get_top_combos')
    ]
    
    failed_imports = []
    
    for module_path, attr in modules_to_test:
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, attr):
                print(f"✅ {module_path}.{attr} - OK")
            else:
                print(f"⚠️  {module_path}.{attr} - ATTRIBUTE NOT FOUND")
                failed_imports.append(f"{module_path}.{attr}")
        except ImportError as e:
            print(f"❌ {module_path} - IMPORT FAILED: {e}")
            failed_imports.append(module_path)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {failed_imports}")
        return False
    
    return True

def main():
    """Run all validation checks."""
    print("🔍 Brand Mixologist - Setup Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Package Initialization", check_init_files),
        ("Environment Variables", check_environment_variables),
        ("Module Imports", check_imports)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} - ERROR: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Validation Results:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Setup validation successful! You can now run the project.")
        print("\nNext steps:")
        print("1. Run data pipeline: python main.py")
        print("2. Start web app: python -m src.frontend.app")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before proceeding.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
