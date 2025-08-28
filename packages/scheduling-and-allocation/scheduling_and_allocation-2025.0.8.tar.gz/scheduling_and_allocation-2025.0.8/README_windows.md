## Windows

### Python Installation

Go to [python site](https://www.python.org/) and navigate to the `Downloads` page

<img src="./document_images/python_download.png" alt="image-20250823111349808" style="zoom:33%;" />

Follow instructions for standard install

* Select admin privileges if you have them, 
* Select `add Python to path`
* **PAY VERY CLOSE ATTENTION TO WHERE IT IS INSTALLED!!**

<img src="./document_images/python_install.png" style="zoom:50%;" />



### Validation

Open a `cmd` window (got to windows search bar and type `cmd`)

<img src="./document_images/python_command_prompt.png" style="zoom:50%;" />

In the command window, type `where python`

<img src="./document_images/python_verify_version.png" style="zoom:75%;" />

The first version of python should be the one you just installed.  

If the above does not show the version of python that you installed, modify the path by...

* Open a `cmd` window
* Type `setx "c:\Users\SandyLocal\AppData\Local\Programs\Python\Python313\python.exe;%PATH"` **but** use the location where *you* saved the the `python.exe` file.

Validate again.

> NOTE: if the above doesn't work, all is not lost, but the easiest method is to ask your administrator to adjust the PATH environment variables on your computer to point to the correct location of python

## Application Installation

Open a `cmd` window (got to windows search bar and type `cmd`)

Type the following in the command window

```bash
python3 -m pip install scheduling_and_allocation
```

## Running the program(s)

Open a `cmd` window (got to windows search bar and type `cmd`)

Type the following in the command window

```bash
Scheduler
```

or

```python
Allocation
```

