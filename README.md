# gitdir

- Minimal and colorful output 🌈 <img src="https://user-images.githubusercontent.com/27065646/71288165-9914bc80-236a-11ea-853b-a97bff999e79.gif" align="right">
- Works on **Linux**, **MacOS**, and **Windows**
<br>
<br>
<br>
<br>
<br>
<br><br>
<br><br>
<br>

## Install 
```bash
$ pip3 install --user gitdir

# Yes, thats all :)
```

## Usage
```
usage: gitdir [-h] [--output_dir OUTPUT_DIR] [--flatten] urls [urls ...]

Download directories/folders from GitHub

positional arguments:
  urls                  List of Github directories to download.

optional arguments:
  -h, --help            show this help message and exit
  --output_dir OUTPUT_DIR, -d OUTPUT_DIR
                        All directories will be downloaded to the specified
                        directory.
  --flatten, -f         Flatten directory structures. Do not create extra
                        directory and download found files to output
                        directory. (default to current directory if not
                        specified)
```

## Packge Entry

You can use `python -m gitdir` / `python3 -m gitdir` in case the short command does not work.

**Exiting**

To exit the program, just press ```CTRL+C```.

## License
MIT License

Copyright (c) 2019 Siddharth Dushantha
