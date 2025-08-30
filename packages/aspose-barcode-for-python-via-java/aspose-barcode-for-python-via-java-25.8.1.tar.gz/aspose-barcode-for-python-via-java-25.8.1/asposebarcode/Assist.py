from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List, Union
import jpype

class BaseJavaClass(ABC):

    def __init__(self, javaClass) -> None:
        if javaClass is None:
            raise ValueError("javaClass cannot be None")
        self.javaClass = javaClass
        self.javaClassName: str = ""

        if not self.javaClassName:
            self.javaClassName = str(self.javaClass.getClass().getName())
        self.init()

    @abstractmethod
    def init(self) -> None:
        pass

    def getJavaClass(self):
        return self.javaClass

    def setJavaClass(self, javaClass) -> None:
        self.javaClass = javaClass
        self.init()

    def getJavaClassName(self) -> str:
        return self.getJavaClass().getClass().getName()

    def isNull(self) -> bool:
        return self.javaClass.isNull()

    def printJavaClassName(self) -> None:
        print("Java class name => \'" + self.javaClassName + "\'")


class Rectangle(BaseJavaClass):
    """!
    A Rectangle specifies an area in a coordinate space that is
    enclosed by the Rectangle object's upper-left point
    in the coordinate space, its width, and its height.
    """

    javaClassName = "java.awt.Rectangle"

    def init(self) -> None:
        pass

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """!
        Rectangle constructor.
        @param x The x-coordinate of the upper-left corner of the rectangle.
        @param y The y-coordinate of the upper-left corner of the rectangle.
        @param width The width of the rectangle.
        @param height The height of the rectangle.
        """
        javaRectangle = jpype.JClass(self.javaClassName)
        self.javaClass = javaRectangle(x, y, width, height)
        super().__init__(self.javaClass)

    def __str__(self) -> str:
        return f"{self.getX()},{self.getY()},{self.getWidth()},{self.getHeight()}"

    def __eq__(self, other: Optional[Rectangle]) -> bool:
        """!
		Determines whether this instance and a specified object,
		which must also be a Unit object, have the same value.
		@param other: The Unit to compare to this instance.
		@return: True if other is a Unit and its value is the same as this instance, otherwise False. If other is None, the method returns false.
		"""
        if other is None:
            return False
        if not isinstance(other, Rectangle):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())


    @staticmethod
    def construct(arg) -> Rectangle:
        rectangle = Rectangle(0, 0, 0, 0)
        rectangle.javaClass = arg
        return rectangle

    def getX(self) -> int:
        """!
        Returns the X coordinate of the bounding Rectangle in
        double precision.
        @return the X coordinate of the bounding Rectangle.
        """
        return int(self.getJavaClass().getX())

    def getY(self) -> int:
        """!
        Returns the Y coordinate of the bounding Rectangle in
        double precision.
        @return the Y coordinate of the bounding Rectangle.
        """
        return int(self.getJavaClass().getY())

    def getLeft(self) -> int:
        """!
        Gets the x-coordinate of the left edge of self Rectangle class.
        @returns The x-coordinate of the left edge of self Rectangle class.
        """
        return self.getX()

    def getTop(self) -> int:
        """!
        Gets the y-coordinate of the top edge of self Rectangle class.
        @returns The y-coordinate of the top edge of self Rectangle class.
        """
        return self.getY()

    def getRight(self) -> int:
        """!
        Gets the x-coordinate that is the sum of X and Width property values of self Rectangle class.
        @returns The x-coordinate that is the sum of X and Width of self Rectangle.
        """
        return self.getX() + self.getWidth()

    def getBottom(self) -> int:
        """!
        Gets the y-coordinate that is the sum of the Y and Height property values of self Rectangle class.
        @returns The y-coordinate that is the sum of Y and Height of self Rectangle.
        """
        return self.getY() + self.getHeight()

    def getWidth(self) -> int:
        """!
        Returns the width of the bounding Rectangle in
        double precision.
        @return the width of the bounding Rectangle.
        """
        return int(self.getJavaClass().getWidth())

    def getHeight(self) -> int:
        """!
        Returns the height of the bounding Rectangle in
        double precision.
        @return the height of the bounding Rectangle.
        """
        return int(self.getJavaClass().getHeight())

    def intersectsWithInclusive(self, rectangle: Rectangle) -> bool:
        """!
       Determines if self rectangle intersects with rect.
       @param rectangle
       @returns {boolean
        """
        return not ((self.getLeft() > rectangle.getRight()) | (self.getRight() < rectangle.getLeft()) |
                    (self.getTop() > rectangle.getBottom()) | (self.getBottom() < rectangle.getTop()))

    @staticmethod
    def intersect(a: Rectangle, b: Rectangle) -> Rectangle:
        """!
        Intersect Shared Method
        Produces a new Rectangle by intersecting 2 existing
        Rectangles. Returns None if there is no    intersection.
        """
        if not a.intersectsWithInclusive(b):
            return Rectangle(0, 0, 0, 0)

        return Rectangle.fromLTRB(max(a.getLeft(), b.getLeft()),
                                  max(a.getTop(), b.getTop()),
                                  min(a.getRight(), b.getRight()),
                                  min(a.getBottom(), b.getBottom()))

    @staticmethod
    def fromLTRB(left: int, top: int, right: int, bottom: int) -> Rectangle:
        """!
        FromLTRB Shared Method
        Produces a Rectangle class from left, top, right,
        and bottom coordinates.
        """
        return Rectangle(left, top, right - left, bottom - top)

    def isEmpty(self) -> bool:
        return (self.getWidth() <= 0) | (self.getHeight() <= 0)


class Point(BaseJavaClass):
    javaClassName = "java.awt.Point"

    def __init__(self, x: int, y: int) -> None:
        javaPoint = jpype.JClass(Point.javaClassName)
        self.javaClass = javaPoint(int(x), int(y))
        super().__init__(self.javaClass)

    @staticmethod
    def construct(arg) -> Point:
        point = Point(0, 0)
        point.javaClass = arg
        return point

    def init(self) -> None:
        pass

    def getX(self) -> int:
        """!
        The X coordinate of this <code>Point</code>.
        If no X coordinate is set it will default to 0.
        """
        return int(self.getJavaClass().getX())

    def getY(self) -> int:
        """!
        The Y coordinate of this <code>Point</code>.
         If no Y coordinate is set it will default to 0.
        """
        return int(self.getJavaClass().getY())

    def setX(self, x: int) -> None:
        """!
        The Y coordinate of this <code>Point</code>.
         If no Y coordinate is set it will default to 0.
        """
        self.getJavaClass().x = x

    def setY(self, y: int) -> None:
        """!
        The Y coordinate of this <code>Point</code>.
         If no Y coordinate is set it will default to 0.
        """
        self.getJavaClass().y = y

    def __str__(self) -> str:
        return f"{self.getX()},{self.getY()}"

    def __eq__(self, other: Optional[Point]) -> bool:
        """!
        Determines whether this instance and a specified object,
        which must also be a Unit object, have the same value.
        @param other: The Unit to compare to this instance.
        @return: True if other is a Unit and its value is the same as this instance, otherwise False. If other is None, the method returns false.
        """
        if other is None:
            return False
        if not isinstance(other, Point):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())


class License(BaseJavaClass):
    javaClassName = "com.aspose.python.barcode.license.PythonLicense"

    def __init__(self) -> None:
        javaLicense = jpype.JClass(self.javaClassName)
        self.javaClass = javaLicense()
        super().__init__(self.javaClass)

    def setLicense(self, filePath: str) -> None:
        """
        Licenses the component.
        @:param: filePath:  Can be a full or short file name. Use an empty string to switch to evaluation mode.
        """
        try:
            file_data = License.openFile(filePath)
            jArray = jpype.JArray(jpype.JString, 1)(file_data)
            self.getJavaClass().setLicense(jArray)
        except Exception as ex:
            raise BarCodeException(ex)

    def isLicensed(self) -> bool:
        javaClass = self.getJavaClass()
        is_licensed = javaClass.isLicensed()
        return str(is_licensed) == "true"

    def resetLicense(self) -> None:
        javaClass = self.getJavaClass()
        javaClass.resetLicense()

    @staticmethod
    def openFile(filename: str) -> List[str]:
        file = open(filename, "rb")
        image_data_binary = file.read()
        file.close()
        array = []
        array.append('')
        i = 0
        while i < len(image_data_binary):
            array.append(str(image_data_binary[i]))
            i += 1
        return array

    def init(self) -> None:
        pass


class BarCodeException(Exception):
    """!
    Represents the exception for creating barcode image.
    """

    @staticmethod
    def MAX_LINES() -> int:
        return 4

    def __init__(self, exc: Union[str, Exception]) -> None:
        """!
        Initializes a new instance of the  BarCodeException class with specified error message.
        """
        self.message: Optional[str] = None
        super().__init__(self, exc)
        if isinstance(exc, str):
            self.setMessage(str(exc))
            return

        exc_message = 'Exception occurred in file:line\n'
        self.setMessage(exc_message)

    def setMessage(self, message: str) -> None:
        """!
        Sets message
        """
        self.message = message

    def getMessage(self) -> Optional[str]:
        """!
        Gets message
        """
        return self.message
