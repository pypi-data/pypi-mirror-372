import sys

# A clear, loud warning message that will be visible in logs.
WARNING_MESSAGE = """
\n
=======================================================================
 WARNING: You have installed a dummy security package.
=======================================================================

The package 'my-internal-package' is a placeholder to prevent
dependency confusion attacks. It contains no code and should not
be installed or used.

Please remove it from your project's dependencies.
If you are part of our organization, use our internal package feed.

=======================================================================
\n
"""

# Print the warning to stderr so it's more likely to be noticed.
sys.stderr.write(WARNING_MESSAGE)

# You can also raise an ImportError to make sure any script using it fails immediately.
raise ImportError("This is a dummy package. See the warning message above.")