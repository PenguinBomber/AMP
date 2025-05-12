# Process

For each mark, AMP performs the following actions in order

1. It pulls the first PDF it finds from the input folder with a name that matches the drawing as defined in the input CSV, and puts it into the output folder
2. It pulls the DSTV matching the piecemark and places it into the output folder. This only goes off of the file name, it **does not** check the header information
3. The DSTV file is "processed" by AMP. This can mean a number of things as defined by the config.json in the same folder as the binary

## TODO

Write the documentation for the configuration