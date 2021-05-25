# coding: utf-8

""" Docstring of :mod:`format.google.foo` module.
"""

foo_var = []
""" Docstring of module variable :any:`format.google.foo.foo_var`."""


def function(arg1, arg2, arg3, arg4):
    """ Docstring of :func:`format.google.foo.function` function.

    Args:
        arg1 (int or str): Parameter arg1 of :func:`format.google.foo.function`.
        arg2 (float): Parameter arg2 of :func:`format.google.foo.function`.
        arg3 (boolean): Parameter arg3 of :func:`format.google.foo.function`.
        arg4 (str): Parameter arg4 of :func:`format.google.foo.function`.
    """
    pass


class Foo(object):
    """ Docstring of :class:`format.google.foo.Foo` class in google format.

    Attributes:
        attr (:class:`~format.rst.enum.EnumFoo`): Docstring of :any:`format.google.foo.Foo.attr` from class docstring.

    Arguments:
        init_arg1 (float): Parameter init_arg1 from class docstring.
        init_arg2 (list[int]): Parameter init_arg2 from class docstring.

    :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
        training. For example, when using a Azure storage blob URI, use the prefix to restrict sub
        folders for training.
    :keyword bool include_subfolders: A flag to indicate if subfolders within the set of prefix folders
        will also need to be included when searching for content to be preprocessed. Not supported if
        training with labels.
    :keyword str model_name: An optional, user-defined name to associate with your model.
    :keyword str continuation_token: A continuation token to restart a poller from a saved state.
    """

    attr = 1
    """ Docstring of :any:`format.google.foo.Foo.attr` from attrbute docstring."""

    def __init__(self, init_arg1, init_arg2):
        """ Docstring of constructor of :class:`format.google.foo.Foo`.

        Parameters:
            init_arg1 (float or\n str): Parameter init_arg1 from constructor's docstring.
            init_arg2 (list[int]): Parameter init_arg2 from constructor's docstring.
        """

    @property
    def attr_getter(self):
        """
        Final result returned by a dialog that just completed.

        :return: Final result returned by a dialog that just completed.
        :rtype: object

        """
        return self.attr

    @classmethod
    def class_method(self, receipt, **kwargs):
        """Extract field text and semantic values from a given sales receipt.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png', 'image/tiff' or 'image/bmp'.

        See fields found on a receipt here:
        https://aka.ms/formrecognizer/receiptfields

        :param telemetry_properties: Additional properties to be logged to telemetry with the LuisResult event, defaults
         to None.
        :type telemetry_properties: :class:`typing.Dict[str, str]`, optional
        """
        pass

    @staticmethod
    def static_method():
        """ Docstring of :meth:`format.google.foo.Foo.static_method` @staticmethod.
        """
        pass

    def method(self):
        """ Docstring of normal class method :meth:`format.google.foo.Foo.method`.
        """
        pass

    def method_return(self):
        """ Docstring of :meth:`format.google.foo.Foo.method_return`.

        Return:
            bool: This method returns a value.
        """
        return False

    def method_multiline(self):
        """ Docstring of :meth:`format.google.foo.Foo.method_multiline`.
        This docstring has multiple lines of contents.
        And this should work perfectly.
        """
        pass

    def method_exception(self):
        """ Docstring of :meth:`format.google.foo.Foo.method_exception`.

        Raises:
            format.rst.foo.FooException: This function raises
            exception.
        """
        raise FooException()

    def method_external_link(self):
        """ Docstring of :meth:`format.google.foo.Foo.method_external_link`.
        Inline link should be transformed to markdown: `Link Text <http://inline.external.link>`_.
        And seperated link will fail: `Seprated Link`_

        .. _Seprated Link: http://seperated.external.link
        """
        pass

    def method_seealso(self):
        """ Docstring of :meth:`format.google.foo.Foo.method_seealso`.

        See Also:
            Seealso contents.
            Multi-line should be supported.
        """
        pass

    def method_note(self):
        """ Docstring of :meth:`format.google.foo.Foo.method_note`.

        Note:
            This is content of note.
            Another line of note contents.
        """
        pass

    def method_warning(self):
        """ Docstring of :meth:`format.google.foo.Foo.method_warning`.

        Warning:
            This is content of warning.
        """
        pass

    def method_code(self):
        """ Docstring of :meth:`format.google.foo.Foo.method_code`.

        .. code-block:: python

            >>> import numpy as np
            >>> a = np.ndarray([1,2,3,4,5])

        Another way of code block::

            >>> import numpy as np
            >>> b = np.random.random(10)
        """
        pass

    def method_example(self):
        """ Docstring of :meth:`format.google.foo.Foo.method_example`.

        Example:
            This is example content.
            Should support multi-line.
            Can also include file:

            .. literalinclude:: ../format/rst/enum.py
        """
        pass


class FooException(Exception):
    """ Docstring of :class:`format.google.foo.FooException`.
    Another class of :mod:`format.google.foo` module.
    """

    class InternalFoo(object):
        """ Docstring of internal class :class:`format.google.foo.FooException.InternalFoo`.
        This class is an internal class of :class:`format.google.foo.FooException`.
        """
        pass
