### Meta data file access.

Install zod package https://github.com/zenseact/zod/tree/main, also available at pypi.

More information about the dataset can be found here: https://zod.zenseact.com/

You should have a folder structure something like `$HOME/zod/sequences/seq_0000`
Under `/zod/` you should have the `train_val` file which finds all the paths, etc., using this you can instantiate all the metadata like.

`sequences = ZodSequences('$HOME/zod',version="mini")`

Where version is `mini` or `full` depending on how much of the dataset you have downloaded.

### Pointcloud conversion

Their pointclouds are stored as .npy, and we covvert them inline. 

Their point timestamps are relative to the frame timestamp, that is the only things that has been modified.
