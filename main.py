import sys
import argparse
from src.doha_validator import validate_doha

def main():
    parser = argparse.ArgumentParser(description="Hindi/Urdu Doha Meter Checker")
    parser.add_argument("input", nargs='?', help="Text string or file path")
    parser.add_argument("--file", "-f", action="store_true", help="Treat input as file path")
    
    args = parser.parse_args()
    
    text = ""
    if not args.input:
        # Read from stdin
        print("Enter Doha text (Press Ctrl+D to finish):")
        text = sys.stdin.read()
    elif args.file:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    else:
        text = args.input
        
    print("\nProcessing...\n")
    
    is_valid, report = validate_doha(text)
    
    print(report)
    print("\nResult:", "VALID DOHA ✅" if is_valid else "INVALID ❌")

if __name__ == "__main__":
    main()
