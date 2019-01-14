Introduction
============

``copypl`` is a Python 3 script to copy the files referenced by a playlist
(M3U, M3U8, or PLS) to a destination folder while retaining the folder structure
of the original locations.  By default, the playlist file is also copied; if the
locations in the playlist are relative to the playlist, this means the copied
playlist file will be correctly referencing the copied files.

Since this tool is intended for copying audio playlists, by default it will also
copy JPEG and PNG files (cover art images, presumably) contained in the same
folders that contain the files referenced by the playlist.  An argument allows
modification of additional file extensions to copy.  Regardless of original
intent, this tool should also work well with playlists containing video or other
file types.  However, for security and simplicity sake, it only works with local
files contained within the folder containing the playlist file, or a subfolder.

A folder heirarchy is created in the destination folder relative to the playlist
folder.

Usage
=====

By default, ``copypl`` will copy the files referenced by a playlist, any JPEG
and PNG files in referenced folders, and the playlist file itself to a
destination folder::

    copypl /share/Music/Favorites.m3u8 /mnt/sdcard

Or on Windows::

    copypl C:\Music\Favorites.m3u8 D:\
    
The folders created at the destination mimic the folders relative to the source
playlist file.  For example, suppose the playlist in the first example above
contained the following entries::

    Popular/Releases/Heap, Imogen/Ellipse/113 - Half Life.ogg
    /share/Music/Popular/Releases/Rush/2112/01 - 2112.ogg

Also suppose that the Ellipse and 2112 folders contained a ``cover.jpg`` file.
The destination would like like so::

    /mnt/sdcard/Favorites.m3u8
    /mnt/sdcard/Popular/Releases/Heap, Imogen/Ellipse/113 - Half Life.ogg
    /mnt/sdcard/Popular/Releases/Heap, Imogen/Ellipse/cover.jpg
    /mnt/sdcard/Popular/Releases/Rush/2112/01 - 2112.ogg
    /mnt/sdcard/Popular/Releases/Rush/2112/cover.jpg

The playlist file can be excluded from the copy using the ``--copy-playlist``
argument.  Copy of related files can be controlled by the ``--extra-extension``
argument, but note that any argument passed will clear the defaults.  Finally,
by default, for efficiency, ``copypl`` will check modification timestamps of
the source and destination files, and only overwrite older destination files.
In addition, it will output a warning if an existing destination file is
newer than the source file.  Use the ``--ignore-mtime`` to always overwrite.
Note that this may cause files to get copied multiple times, e.g., if the
playlist references multiple files in a folder, then the extra files in the
folder will get copied repeatedly.

Installation
============

.. warning::

    Some Linux distributions discourage installation of system-level python
    packages using ``pip`` or ``setup.py install``, due to collisions with the
    system package manager.  In those cases, dependencies should be installed
    through the package manager, if possible, or choose a user folder
    installation method.

Installing with pip
-------------------

If your system has ``pip`` installed, and you have access to install software in
the system packages, then *kantag* kan be installed as administrator from 
`PyPI <https://pypi.python.org/pypi>`_::

    # pip install copypl

If you do not have access to install system packages, or do not wish to install
in the system location, it can be installed in a user folder::

    $ pip install --user copypl

Installing from source
----------------------

Either download a release tarball from the
`Downloads <https://bitbucket.org/dgasaway/copypl/downloads/>`_ page, and
unpack::

    $ tar zxvf copypl-1.0.0.tar.gz

Or get the latest source from the Mercurial repository::

    $ hg clone https://bitbucket.org/dgasaway/copypl

If you have access to install software in the system packages, then it can be
installed as administrator::

    # python setup.py install

If you do not have access to install system packages, or do not wish to install
in the system location, it can be installed in a user folder::

    $ python setup.py install --user
