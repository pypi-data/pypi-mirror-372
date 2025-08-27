Installation
============

ggoat is designed to be lightweight and easy to install across different Python environments.

Quick Installation
------------------

**Standard Python**::

    pip install ggoat

**Development Installation**::

    git clone https://github.com/ggoat/ggoat.git
    cd ggoat
    pip install -e .

**Pyodide Environment**::

    import micropip
    await micropip.install("ggoat")

Requirements
-----------

**Minimal Requirements**:
    * Python 3.7+
    * No additional dependencies required

**Optional Dependencies**:
    * ``pandas`` - For DataFrame support
    * ``numpy`` - For enhanced numerical operations  
    * ``lets-plot`` - For native lets-plot integration in Jupyter

Environment-Specific Setup
--------------------------

Jupyter Notebooks
~~~~~~~~~~~~~~~~~

For full Jupyter integration::

    pip install ggoat lets-plot
    
Then in your notebook::

    import lets_plot as lp
    lp.LetsPlot.setup_html()  # Enable lets-plot rendering
    
    from ggoat import ggplot, aes

Pyodide/WebAssembly
~~~~~~~~~~~~~~~~~~

ggoat is optimized for Pyodide environments::

    # In your web page
    <script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
    
    <script>
    async function main() {
        let pyodide = await loadPyodide();
        await pyodide.loadPackage("micropip");
        await pyodide.runPython(`
            import micropip
            await micropip.install("ggoat")
            
            from ggoat import ggplot, aes
            # Your plotting code here
        `);
    }
    main();
    </script>

Google Colab
~~~~~~~~~~~~

ggoat works out-of-the-box in Google Colab::

    !pip install ggoat
    
    from ggoat import ggplot, aes

JupyterLite
~~~~~~~~~~~

For JupyterLite (browser-based Jupyter)::

    %pip install ggoat
    
    from ggoat import ggplot, aes

Verification
-----------

Test your installation::

    from ggoat import ggplot, aes
    
    # Create test data
    data = {'x': [1, 2, 3], 'y': [4, 5, 6]}
    
    # Create and show plot
    plot = ggplot(data, aes(x='x', y='y')).geom_point()
    plot.show()

If you see a plot output, ggoat is working correctly!

Troubleshooting
--------------

**Import Errors**
    Ensure Python 3.7+ is being used::
    
        python --version

**Missing lets-plot Integration**
    Install lets-plot for enhanced Jupyter support::
    
        pip install lets-plot

**Pyodide Issues**
    Ensure you're using a compatible Pyodide version (0.20+)

**Performance in Large Datasets**
    Consider using pandas for better performance::
    
        pip install pandas

Getting Help
-----------

* **Documentation**: https://ggoat.readthedocs.io
* **Issues**: https://github.com/ggoat/ggoat/issues  
* **Discussions**: https://github.com/ggoat/ggoat/discussions

Next Steps
----------

* :doc:`getting_started` - Create your first plots
* :doc:`tutorials/index` - Learn ggoat step by step
* :doc:`examples/basic_plots` - Ready-to-use examples