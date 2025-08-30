from __future__ import annotations

from abc import abstractmethod
from typing import Union, List, Optional
import calendar
from datetime import datetime, timezone

import jpype
import base64
import io
from PIL import Image
from enum import Enum
from . import Generation, Assist


class IComplexCodetext(Assist.BaseJavaClass):
    """!
    Interface for complex codetext used with ComplexBarcodeGenerator.
    """

    def __init__(self, javaClass):
        super().__init__(javaClass)
        self.init()

    @abstractmethod
    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Construct codetext for complex barcode
        @return Constructed codetext
        """
        pass

    @abstractmethod
    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes instance with constructed codetext.
        @param constructedCodetext Constructed codetext.
        """
        raise Assist.BarCodeException(
            'You have to implement the method initFromString!')

    @abstractmethod
    def getBarcodeType(self) -> Generation.EncodeTypes:
        """!
        Gets barcode type.
        @return Barcode type.
        """
        raise Assist.BarCodeException(
            'You have to implement the method getBarcodeType!')


class ComplexBarcodeGenerator(Assist.BaseJavaClass):
    """!
    ComplexBarcodeGenerator for backend complex barcode (e.g. SwissQR) images generation.
    This sample shows how to create and save a SwissQR image.
      \code
        swissQRCodetext = ComplexBarcode.SwissQRCodetext(None)
        swissQRCodetext.getBill().setAccount("CH450023023099999999A")
        swissQRCodetext.getBill().setBillInformation("BillInformation")
        swissQRCodetext.getBill().setAmount(1024)
        swissQRCodetext.getBill().getCreditor().setName("Creditor.Name")
        swissQRCodetext.getBill().getCreditor().setAddressLine1("Creditor.AddressLine1")
        swissQRCodetext.getBill().getCreditor().setAddressLine2("Creditor.AddressLine2")
        swissQRCodetext.getBill().getCreditor().setCountryCode("Nl")
        swissQRCodetext.getBill().setUnstructuredMessage("UnstructuredMessage")
        swissQRCodetext.getBill().setReference("Reference")
        swissQRCodetext.getBill().setAlternativeSchemes([ComplexBarcode.AlternativeScheme(
            "AlternativeSchemeInstruction1"), ComplexBarcode.AlternativeScheme("AlternativeSchemeInstruction2")])
        swissQRCodetext.getBill().setDebtor(ComplexBarcode.Address())
        swissQRCodetext.getBill().getDebtor().setName("Debtor.Name")
        swissQRCodetext.getBill().getDebtor().setAddressLine1("Debtor.AddressLine1")
        swissQRCodetext.getBill().getDebtor().setAddressLine2("Debtor.AddressLine2")
        swissQRCodetext.getBill().getDebtor().setCountryCode("LU")
        cg = ComplexBarcode.ComplexBarcodeGenerator(swissQRCodetext)
        res = cg.generateBarCodeImage()
       \endcode
    """
    javaClassName = "com.aspose.mw.barcode.complexbarcode.MwComplexBarcodeGenerator"

    def init(self) -> None:
        pass

    def getParameters(self) -> Generation.BaseGenerationParameters:
        """!
        Generation parameters.
        """
        return self.parameters

    def __init__(self, complexCodetext: IComplexCodetext):
        """!
        Creates an instance of ComplexBarcodeGenerator.
        @param complexCodetext Complex codetext
        """
        try:
            javaComplexBarcodeGenerator = jpype.JClass(ComplexBarcodeGenerator.javaClassName)
            super().__init__(javaComplexBarcodeGenerator(complexCodetext.getJavaClass()))
            self.parameters: Generation.BaseGenerationParameters = Generation.BaseGenerationParameters(self.getJavaClass().getParameters())
        except Exception as e:
            raise Assist.BarCodeException(e)
        self.init()

    def generateBarCodeImage(self) -> Image.Image:
        """!
        Generates complex barcode image under current settings.
        @param value of BarCodeImageFormat (PNG, BMP, JPEG, GIF, TIFF)
        default value is BarCodeImageFormat.PNG
        @return  Pillow Image object of barcode image
        """
        bytes_data = base64.b64decode(str(self.javaClass.generateBarCodeImage(
            Generation.BarCodeImageFormat.PNG.value)))
        buf = io.BytesIO(bytes_data)
        return Image.open(buf)

    def save(self, imageSource: Union[str, io.BytesIO], imageFormat: Generation.BarCodeImageFormat) -> None:
        """!
        Save barcode image to specific file in specific format.
        @param imagePath Path to save to.
        @param imageFormat of BarCodeImageFormat enum (PNG, BMP, JPEG, GIF, TIFF)
            \code
            generator = Generation.BarcodeGenerator(Generation.EncodeTypes.CODE_128, "12345678")
            generator.save(path_to_save, Generation.BarCodeImageFormat.PNG)
            \endcode
        """
        if not isinstance(imageSource, (str, io.BytesIO)):
            raise ValueError("Parameter imageSource must be a string path or a BytesIO object.")

        try:
            # Save the image (to either a file path or BytesIO)
            image = self.generateBarCodeImage()
            image.save(imageSource, imageFormat.name)
        except Exception as e:
            raise IOError(f"Failed to save the image: {e}")


class Address(Assist.BaseJavaClass):
    """!
    Address of creditor or debtor.
      You can either set street, house number, postal code and town (type structured address)
      or address line 1 and 2 (type combined address elements). The type is automatically set
      once any of these fields is set. Before setting the fields, the address type is undetermined.
      If fields of both types are set, the address type becomes conflicting.
      Name and country code must always be set unless all fields are empty.
    """
    javaClassName = "com.aspose.mw.barcode.complexbarcode.MwAddress"

    def __init__(self) -> None:
        jclass = jpype.JClass(Address.javaClassName)
        super().__init__(jclass())
        self.init()

    @staticmethod
    def construct(javaClass) -> Address:
        address = Address()
        address.setJavaClass(javaClass)
        address.init()
        return address

    def getType(self) -> AddressType:
        """!
        Gets the address type.
            The address type is automatically set by either setting street / house number
            or address line 1 and 2. Before setting the fields, the address type is Undetermined.
            If fields of both types are set, the address type becomes Conflicting.
            @return: The address type.
        """
        return AddressType(self.getJavaClass().getType())

    def getName(self) -> Optional[str]:
        """!
                Gets the name, either the first and last name of a natural person or the
                company name of a legal person.
                @return:The name.
                """
        name = self.getJavaClass().getName()
        return str(name) if name is not None else None

    def setName(self, value: Optional[str]) -> None:
        """!
        Sets the name, either the first and last name of a natural person or the
        company name of a legal person.
        @param:The name.
        """
        self.getJavaClass().setName(value)

    def getAddressLine1(self) -> Optional[str]:
        """!
        Gets the address line 1.
        Address line 1 contains street name, house number or P.O. box.
        Setting this field sets the address type to AddressType.CombinedElements unless it's already
        AddressType.Structured, in which case it becomes AddressType.Conflicting.
        This field is only used for combined elements addresses and is optional.
        @return:The address line 1.
       """
        address_line1 = self.getJavaClass().getAddressLine1()
        return str(address_line1) if address_line1 is not None else None

    def setAddressLine1(self, value: Optional[str]) -> None:
        """!
        Sets the address line 1.
        Address line 1 contains street name, house number or P.O. box.
        Setting this field sets the address type to AddressType.CombinedElements unless it's already
        AddressType.Structured, in which case it becomes AddressType.Conflicting.
        This field is only used for combined elements addresses and is optional.
        @param:The address line 1.
        """
        self.getJavaClass().setAddressLine1(value)

    def getAddressLine2(self) -> Optional[str]:
        """!
        Gets the address line 2.
        Address line 2 contains postal code and town.
        Setting this field sets the address type to AddressType.CombinedElements unless it's already
        AddressType.Structured, in which case it becomes AddressType.Conflicting.
        This field is only used for combined elements addresses. For this type, it's mandatory.
        @return: The address line 2.
        """
        address_line2 = self.getJavaClass().getAddressLine2()
        return str(address_line2) if address_line2 is not None else None

    def setAddressLine2(self, value: Optional[str]) -> None:
        """!
        Sets the address line 2.
        Address line 2 contains postal code and town.
        Setting this field sets the address type to AddressType.CombinedElements unless it's already
        AddressType.Structured, in which case it becomes AddressType.Conflicting.
        This field is only used for combined elements addresses. For this type, it's mandatory.
        @param:The address line 2.
        """
        self.getJavaClass().setAddressLine2(value)

    def getStreet(self) -> Optional[str]:
        """!
        Gets the street.
        The street must be speicfied without house number.
        Setting this field sets the address type to AddressType.Structured unless it's already
        AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
        This field is only used for structured addresses and is optional.
        @return:The street.
        """
        street = self.getJavaClass().getStreet()
        return str(street) if street is not None else None

    def setStreet(self, value: Optional[str]) -> None:
        """!
        Sets the street.
        The street must be speicfied without house number.
        Setting this field sets the address type to AddressType.Structured unless it's already
        AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
        This field is only used for structured addresses and is optional.
        @param:The street.
        """
        self.getJavaClass().setStreet(value)

    def getHouseNo(self) -> Optional[str]:
        """!
        Gets the house number.
        Setting this field sets the address type to AddressType.Structured unless it's already
        AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
        This field is only used for structured addresses and is optional.
        @return:The house number.
        """
        house_no = self.getJavaClass().getHouseNo()
        return str(house_no) if house_no is not None else None

    def setHouseNo(self, value: Optional[str]) -> None:
        """!
        Sets the house number.
        Setting this field sets the address type to AddressType.Structured unless it's already
        AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
        This field is only used for structured addresses and is optional.
        @param:The house number.
        """
        self.getJavaClass().setHouseNo(value)

    def getPostalCode(self) -> Optional[str]:
        """!
        Gets the postal code.
        Setting this field sets the address type to AddressType.Structured unless it's already
        AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
        This field is only used for structured addresses. For this type, it's mandatory.
        @return:The postal code.
       """
        postal_code = self.getJavaClass().getPostalCode()
        return str(postal_code) if postal_code is not None else None

    def setPostalCode(self, value: Optional[str]) -> None:
        """!
        Sets the postal code.
        Setting this field sets the address type to AddressType.Structured unless it's already
        AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
        This field is only used for structured addresses. For this type, it's mandatory.
        @param:The postal code.
        """
        self.getJavaClass().setPostalCode(value)

    def getTown(self) -> Optional[str]:
        """!
        Gets the town or city.
        Setting this field sets the address type to AddressType.Structured unless it's already
        AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
        This field is only used for structured addresses. For this type, it's mandatory.
        @return:The town or city.
       """
        town = self.getJavaClass().getTown()
        return str(town) if town is not None else None

    def setTown(self, value: Optional[str]) -> None:
        """!
        Sets the town or city.
        Setting this field sets the address type to AddressType.Structured unless it's already
        AddressType.CombinedElements, in which case it becomes AddressType.Conflicting.
        This field is only used for structured addresses. For this type, it's mandatory.
        @param:The town or city.
        """
        self.getJavaClass().setTown(value)

    def getCountryCode(self) -> Optional[str]:
        """!
        Gets the two-letter ISO country code.
        The country code is mandatory unless the entire address contains None or emtpy values.
        @return:The ISO country code.
       """
        country_code = self.getJavaClass().getCountryCode()
        return str(country_code) if country_code is not None else None

    def setCountryCode(self, value: Optional[str]) -> None:
        """!
        Sets the two-letter ISO country code.
        The country code is mandatory unless the entire address contains None or emtpy values.
        @param:The ISO country code.
        """
        self.getJavaClass().setCountryCode(value)

    def clear(self) -> None:
        """!
        Clears all fields and sets the type to AddressType.Undetermined.
        """
        self.setName(None)
        self.setAddressLine1(None)
        self.setAddressLine2(None)
        self.setStreet(None)
        self.setHouseNo(None)
        self.setPostalCode(None)
        self.setTown(None)
        self.setCountryCode(None)

    def __eq__(self, other: Address) -> bool:
        """!
        Determines whether the specified object is equal to the current object.
        @return True if the specified object is equal to the current object; otherwise, false.
        @param obj The object to compare with the current object.
        """
        if other is None:
            return False
        if not isinstance(other, Address):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())

    def init(self) -> None:
        return


class AddressType(Enum):
      """!
      Address type
      """

      # Undetermined
      UNDETERMINED = 0

      # Structured address
      STRUCTURED = 1

      # Combined address elements
      COMBINED_ELEMENTS = 2

      # Conflicting
      CONFLICTING = 3


class AlternativeScheme(Assist.BaseJavaClass):
    """!
	Alternative payment scheme instructions
	"""
    javaClassName = "com.aspose.mw.barcode.complexbarcode.MwAlternativeScheme"

    def __init__(self, instruction: str) -> None:
        javaAlternativeScheme = jpype.JClass(AlternativeScheme.javaClassName)
        super().__init__(javaAlternativeScheme(instruction))

    @staticmethod
    def construct(javaClass) -> AlternativeScheme:
        jsClass = AlternativeScheme("")
        jsClass.setJavaClass(javaClass)
        return jsClass

    def getInstruction(self) -> str:
        """!
		Gets the payment instruction for a given bill.
		The instruction consists of a two letter abbreviation for the scheme, a separator characters
		and a sequence of parameters(separated by the character at index 2).
		@return:The payment instruction.
		"""
        value = self.getJavaClass().getInstruction()
        return str(value) if value is not None else None

    def setInstruction(self, value: str) -> None:
        """!
		Gets the payment instruction for a given bill.
		The instruction consists of a two letter abbreviation for the scheme, a separator characters
		and a sequence of parameters(separated by the character at index 2).
		@param:The payment instruction.
		"""
        self.getJavaClass().setInstruction(value)

    def __eq__(self, other: AlternativeScheme) -> bool:
        """!
		Determines whether the specified object is equal to the current object.
		@return True if the specified object is equal to the current object; otherwise, false.
		@param obj The object to compare with the current object.
		"""
        if other is None:
            return False
        if not isinstance(other, AlternativeScheme):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return a hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())

    def init(self) -> None:
        return


class ComplexCodetextReader(Assist.BaseJavaClass):
    """!
	ComplexCodetextReader decodes codetext to specified complex barcode type.
	This sample shows how to recognize and decode SwissQR image.
	 \code
	   barCodeReader = Recognition.BarCodeReader(
	       "SwissQRCodetext.png", None, Recognition.DecodeType.QR)
	   results = barCodeReader.readBarCodes()
	   result = ComplexBarcode.ComplexCodetextReader.tryDecodeSwissQR(
	       results[0].getCodeText())
	 \endcode
	"""
    javaClassName = "com.aspose.mw.barcode.complexbarcode.MwComplexCodetextReader"

    @staticmethod
    def tryDecodeSwissQR(encodedCodetext: str) -> Optional[SwissQRCodetext]:
        """!
		Decodes SwissQR codetext.
		@return decoded SwissQRCodetext or None.
		@param encodedCodetext encoded codetext
		"""
        javaComplexCodetextReaderClass = jpype.JClass(ComplexCodetextReader.javaClassName)
        javaSwissQR = javaComplexCodetextReaderClass.tryDecodeSwissQR(encodedCodetext)
        return None if javaSwissQR is None else SwissQRCodetext.construct(javaSwissQR)

    @staticmethod
    def tryDecodeMailmark2D(encodedCodetext: str) -> Optional[Mailmark2DCodetext]:
        """!
		Decodes Royal Mail Mailmark 2D codetext.
		@param encodedCodetext encoded codetext
		@return decoded Royal Mail Mailmark 2D or None.
		"""
        javaComplexCodetextReaderClass = jpype.JClass(ComplexCodetextReader.javaClassName)
        javaMailmark2DCodetext = javaComplexCodetextReaderClass.tryDecodeMailmark2D(encodedCodetext)
        return None if javaMailmark2DCodetext is None else Mailmark2DCodetext.construct(javaMailmark2DCodetext)

    @staticmethod
    def tryDecodeMailmark(encodedCodetext: str) -> Optional[MailmarkCodetext]:
        """!
		Decodes Mailmark Barcode C and L codetext.
		@param encodedCodetext encoded codetext
		@return Decoded Mailmark Barcode C and L or None.
		"""
        javaComplexCodetextReaderClass = jpype.JClass(ComplexCodetextReader.javaClassName)
        javaDecodeMailmark = javaComplexCodetextReaderClass.tryDecodeMailmark(encodedCodetext)
        return None if javaDecodeMailmark is None else MailmarkCodetext.construct(javaDecodeMailmark)

    @staticmethod
    def tryDecodeMaxiCode(maxiCodeMode: Generation.MaxiCodeMode, encodedCodetext: str) -> Optional[Union[MaxiCodeCodetextMode2, MaxiCodeCodetextMode3, MaxiCodeStandardCodetext]]:
        """!
		Decodes MaxiCode codetext.
		@param: maxiCodeMode:  MaxiCode mode
		@param: encodedCodetext:  encoded codetext
		@return:  Decoded MaxiCode codetext.
		"""
        javaComplexCodetextReaderClass = jpype.JClass(ComplexCodetextReader.javaClassName)
        javaMaxiCodeCodetextMode2Class = jpype.JClass(MaxiCodeCodetextMode2.JAVA_CLASS_NAME)
        javaMaxiCodeCodetextMode3Class = jpype.JClass(MaxiCodeCodetextMode3.JAVA_CLASS_NAME)
        javaMaxiCodeCodetext = javaComplexCodetextReaderClass.tryDecodeMaxiCode(maxiCodeMode.value, encodedCodetext)

        if javaMaxiCodeCodetext.getClass().equals(javaMaxiCodeCodetextMode2Class().getClass()):
            return MaxiCodeCodetextMode2.construct(javaMaxiCodeCodetext)
        elif javaMaxiCodeCodetext.getClass().equals(javaMaxiCodeCodetextMode3Class().getClass()):
            return MaxiCodeCodetextMode3.construct(javaMaxiCodeCodetext)
        else:
            return MaxiCodeStandardCodetext.construct(javaMaxiCodeCodetext)

    @staticmethod
    def tryDecodeHIBCLIC(encodedCodetext: str) -> Optional[Union[HIBCLICSecondaryAndAdditionalDataCodetext, HIBCLICPrimaryDataCodetext, HIBCLICCombinedCodetext]]:
        """!
		Decodes HIBC LIC codetext.
		@param: encodedCodetext:encoded codetext
		@return:decoded HIBC LIC Complex Codetext or None.
		"""
        javaHIBCLICSecondaryAndAdditionalDataCodetextClass = jpype.JClass(HIBCLICSecondaryAndAdditionalDataCodetext.JAVA_CLASS_NAME)
        javaHIBCLICPrimaryDataCodetextClass = jpype.JClass(HIBCLICPrimaryDataCodetext.JAVA_CLASS_NAME)
        javaHIBCLICCombinedCodetextClass = jpype.JClass(HIBCLICCombinedCodetext.JAVA_CLASS_NAME)
        javaPhpComplexCodetextReaderJavaClass = jpype.JClass(ComplexCodetextReader.javaClassName)
        hibclicComplexCodetext = javaPhpComplexCodetextReaderJavaClass.tryDecodeHIBCLIC(encodedCodetext)
        if hibclicComplexCodetext is None:
            return hibclicComplexCodetext
        if hibclicComplexCodetext.getClass().equals(javaHIBCLICSecondaryAndAdditionalDataCodetextClass().getClass()):
            return HIBCLICSecondaryAndAdditionalDataCodetext.construct(hibclicComplexCodetext)
        elif hibclicComplexCodetext.getClass().equals(javaHIBCLICPrimaryDataCodetextClass().getClass()):
            return HIBCLICPrimaryDataCodetext.construct(hibclicComplexCodetext)
        elif hibclicComplexCodetext.getClass().equals(javaHIBCLICCombinedCodetextClass().getClass()):
            return HIBCLICCombinedCodetext.construct(hibclicComplexCodetext)
        return None

    @staticmethod
    def tryDecodeHIBCPAS(encodedCodetext: str) -> Optional[HIBCPASCodetext]:
        """!
		Decodes HIBC PAS codetext.
		@param: encodedCodetext:  encoded codetext
		@return: decoded HIBC PAS Complex Codetext or None.
		"""
        javaComplexCodetextReader = jpype.JClass(ComplexCodetextReader.javaClassName)
        javaHIBCPAS = javaComplexCodetextReader.tryDecodeHIBCPAS(encodedCodetext)
        if javaHIBCPAS is None:
            return None
        return HIBCPASCodetext.construct(javaHIBCPAS)


class QrBillStandardVersion(Enum):
      """!
      SwissQR bill standard version
      """

      # Version 2.0
      V2_0 = 0


class SwissQRBill(Assist.BaseJavaClass):
    """!
	SwissQR bill data
	"""

    def init(self) -> None:
        pass

    def __init__(self, javaClass) -> None:
        super().__init__(javaClass)
        # Initializing data from a Java class
        self.creditor: Address = Address.construct(self.getJavaClass().getCreditor())
        self.debtor: Address = Address.construct(self.getJavaClass().getDebtor())
        self.init()

    @staticmethod
    def convertAlternativeSchemes(javaAlternativeSchemes) -> List[AlternativeScheme]:
        alternativeSchemes = []
        i = 0
        while i < javaAlternativeSchemes.size():
            alternativeSchemes.append(
                AlternativeScheme.construct(javaAlternativeSchemes.get(i)))
            i += 1
        return alternativeSchemes

    def getVersion(self) -> QrBillStandardVersion:
        """!
		Gets the version of the SwissQR bill standard.
		@return:The SwissQR bill standard version.
		"""
        return QrBillStandardVersion(self.getJavaClass().getVersion())

    def setVersion(self, value: QrBillStandardVersion) -> None:
        """!
		Sets the version of the SwissQR bill standard.
		@param:The SwissQR bill standard version.
		"""
        self.getJavaClass().setVersion(value.value)

    def getAmount(self) -> float:
        """!
        Gets the payment amount.
        Valid values are between 0.01 and 999,999,999.99.
        @return:The payment amount.
        """
        return float(self.getJavaClass().getAmount())

    def setAmount(self, value: float) -> None:
        """!
        Sets the payment amount.
        Valid values are between 0.01 and 999,999,999.99.
        @param:The payment amount.
        """
        self.getJavaClass().setAmount(value)

    def getCurrency(self) -> Optional[str]:
        """!
        Gets the payment currency.
        Valid values are "CHF" and "EUR".
        @return:The payment currency.
        """
        currency = self.getJavaClass().getCurrency()
        return str(currency) if currency is not None else None

    def setCurrency(self, value: str) -> None:
        """!
        Sets the payment currency.
        Valid values are "CHF" and "EUR".
        @param:The payment currency.
        """
        self.getJavaClass().setCurrency(value)

    def getAccount(self) -> Optional[str]:
        """!
        Gets the creditor's account number.
        Account numbers must be valid IBANs of a bank of Switzerland or
        Liechtenstein. Spaces are allowed in the account number.
        @return:The creditor account number.
        """
        account = self.getJavaClass().getAccount()
        return str(account) if account is not None else None

    def setAccount(self, value: str) -> None:
        """!
        Sets the creditor's account number.
        Account numbers must be valid IBANs of a bank of Switzerland or
        Liechtenstein. Spaces are allowed in the account number.
        @param:The creditor account number.
        """
        self.getJavaClass().setAccount(value)

    def getCreditor(self) -> Optional[Address]:
        """!
        Gets the creditor address.
        @return:The creditor address.
        """
        return self.creditor

    def setCreditor(self, value: Address) -> None:
        """!
        Sets the creditor address.
        @param:The creditor address.
        """
        self.creditor = value
        self.getJavaClass().setCreditor(value.getJavaClass())

    def getReference(self) -> Optional[str]:
        """!
        Gets the creditor payment reference.
        The reference is mandatory for SwissQR IBANs, i.e.IBANs in the range
        CHxx30000xxxxxx through CHxx31999xxxxx.
        If specified, the reference must be either a valid SwissQR reference
        (corresponding to ISR reference form) or a valid creditor reference
         according to ISO 11649 ("RFxxxx"). Both may contain spaces for formatting.
        @return:The creditor payment reference.
        """
        reference = self.getJavaClass().getReference()
        return str(reference) if reference is not None else None

    def setReference(self, value: str) -> None:
        """!
        Sets the creditor payment reference.
        The reference is mandatory for SwissQR IBANs, i.e.IBANs in the range
        CHxx30000xxxxxx through CHxx31999xxxxx.
        If specified, the reference must be either a valid SwissQR reference
        (corresponding to ISR reference form) or a valid creditor reference
        according to ISO 11649 ("RFxxxx"). Both may contain spaces for formatting.
        @param:The creditor payment reference.
        """
        self.getJavaClass().setReference(value)

    def createAndSetCreditorReference(self, rawReference: str) -> None:
        """!
        Creates and sets a ISO11649 creditor reference from a raw string by prefixing
        the String with "RF" and the modulo 97 checksum.
        Whitespace is removed from the reference
        @exception ArgumentException rawReference contains invalid characters.
        @param rawReference The raw reference.
        """
        self.getJavaClass().createAndSetCreditorReference(rawReference)

    def getDebtor(self) -> Optional[Address]:
        """!
        Gets the debtor address.
        The debtor is optional. If it is omitted, both setting this field to
        None or setting an address with all None or empty values is ok.
        @return:The debtor address.
        """
        return self.debtor

    def setDebtor(self, value: Address) -> None:
        """!
        Sets the debtor address.
        The debtor is optional. If it is omitted, both setting this field to
        None or setting an address with all None or empty values is ok.
        @param:The debtor address.
        """
        self.debtor = value
        self.getJavaClass().setDebtor(value.getJavaClass())

    def getUnstructuredMessage(self) -> Optional[str]:
        """!
        Gets the additional unstructured message.
        @return:The unstructured message.
        """
        message = self.getJavaClass().getUnstructuredMessage()
        return str(message) if message is not None else None

    def setUnstructuredMessage(self, value: str) -> None:
        """!
        Sets the additional unstructured message.
        @param:The unstructured message.
        """
        self.getJavaClass().setUnstructuredMessage(value)

    def getBillInformation(self) -> Optional[str]:
        """!
        Gets the additional structured bill information.
        @return:The structured bill information.
        """
        bill_info = self.getJavaClass().getBillInformation()
        return str(bill_info) if bill_info is not None else None

    def setBillInformation(self, value: str) -> None:
        """!
        Sets the additional structured bill information.
        @param:The structured bill information.
        """
        self.getJavaClass().setBillInformation(value)

    def getAlternativeSchemes(self) -> List[AlternativeScheme]:
        """!
        Gets the alternative payment schemes.
        A maximum of two schemes with parameters are allowed.
        @return:The alternative payment schemes.
        """
        return SwissQRBill.convertAlternativeSchemes(self.getJavaClass().getAlternativeSchemes())

    def setAlternativeSchemes(self, value: List[AlternativeScheme]) -> None:
        """!
		Sets the alternative payment schemes.
		A maximum of two schemes with parameters are allowed.
		@param:The alternative payment schemes.
		"""
        ArrayList = jpype.JClass('java.util.ArrayList')
        javaArray = ArrayList()
        i = 0
        while i < len(value):
            javaArray.add(value[i].getJavaClass())
            i += 1
        self.getJavaClass().setAlternativeSchemes(javaArray)

    def __eq__(self, other: SwissQRBill) -> bool:
        """!
		Determines whether the specified object is equal to the current object.
		@return True if the specified object is equal to the current object; otherwise, false.
		@param obj The object to compare with the current object.
		"""
        if other is None:
            return False
        if not isinstance(other, SwissQRBill):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())


class SwissQRCodetext(IComplexCodetext):
    """!
    Class for encoding and decoding the text embedded in the SwissQR code.
    """
    javaClassName = "com.aspose.mw.barcode.complexbarcode.MwSwissQRCodetext"

    def getBill(self) -> Optional[SwissQRBill]:
        """!
        SwissQR bill data
        """
        return self.bill

    def __init__(self, bill: Optional[SwissQRBill]) -> None:
        """!
        Creates an instance of SwissQRCodetext.
        @param bill SwissQR bill data
        @throws BarCodeException
        """
        javaClass = jpype.JClass(SwissQRCodetext.javaClassName)

        # self.bill: Optional[SwissQRBill] = None
        javaBill = None
        if bill is None:
            javaBill = javaClass()
        else:
            javaBill = javaClass(bill.getJavaClass())
        super().__init__(javaBill)
        self.bill: SwissQRBill = SwissQRBill(self.getJavaClass().getBill())

    def init(self) -> None:
        self.bill = SwissQRBill(self.getJavaClass().getBill())
        pass


    @staticmethod
    def construct(javaClass) -> SwissQRCodetext:
        pythonClass = SwissQRCodetext(None)
        pythonClass.setJavaClass(javaClass)
        return pythonClass

    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Construct codetext from SwissQR bill data
        @return Constructed codetext
        """
        return str(self.getJavaClass().getConstructedCodetext())

    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes Bill with constructed codetext.
        @param constructedCodetext Constructed codetext.
        """
        self.getJavaClass().initFromString(constructedCodetext)
        self.init()

    def getBarcodeType(self) -> Generation.EncodeTypes:
        """!
        Gets barcode type.
        @return Barcode type.
        """
        return Generation.EncodeTypes(self.getJavaClass().getBarcodeType())


class MailmarkCodetext(IComplexCodetext):
    """!
    Class for encoding and decoding the text embedded in the 4-state Royal Mailmark code.
    """
    javaClassName = "com.aspose.mw.barcode.complexbarcode.MwMailmarkCodetext"

    def __init__(self) -> None:
        """!
        Initializes a new instance of the MailmarkCodetext class.
        @param: mailmarkCodetext:
        """
        java_class_link = jpype.JClass(self.javaClassName)
        javaClass = java_class_link()
        super().__init__(javaClass)

    @staticmethod
    def construct(javaClass) -> MailmarkCodetext:
        pythonClass = MailmarkCodetext()
        pythonClass.setJavaClass(javaClass)
        return pythonClass

    def init(self) -> None:
        pass

    def getFormat(self) -> int:
        """!
        "0" – None or Test
        "1" – Letter
        "2" – Large Letter
        """
        return int(self.getJavaClass().getFormat())

    def setFormat(self, value: int) -> None:
        """!
        "0" – None or Test
        "1" – LetterN
        "2" – Large Letter
        """
        self.getJavaClass().setFormat(value)

    def getVersionID(self) -> int:
        """!
        Currently "1" – For Mailmark barcode (0 and 2 to 9 and A to Z spare for future use)
        @return:
        """
        return int(self.getJavaClass().getVersionID())

    def setVersionID(self, value: int) -> None:
        """!
        Currently "1" – For Mailmark barcode (0 and 2 to 9 and A to Z spare for future use)
        """
        self.getJavaClass().setVersionID(value)

    def getClass_(self) -> str:
        """!
        "0" - None or Test
        "1" - 1C (Retail)
        "2" - 2C (Retail)
        "3" - 3C (Retail)
        "4" - Premium (RetailPublishing Mail) (for potential future use)
        "5" - Deferred (Retail)
        "6" - Air (Retail) (for potential future use)
        "7" - Surface (Retail) (for potential future use)
        "8" - Premium (Network Access)
        "9" - Standard (Network Access)
        """
        value = self.getJavaClass().getClass_()
        return str(value) if value is not None else None

    def setClass(self, value: str) -> None:
        """!
        "0" - None or Test
        "1" - 1C (Retail)
        "2" - 2C (Retail)
        "3" - 3C (Retail)
        "4" - Premium (RetailPublishing Mail) (for potential future use)
        "5" - Deferred (Retail)
        "6" - Air (Retail) (for potential future use)
        "7" - Surface (Retail) (for potential future use)
        "8" - Premium (Network Access)
        "9" - Standard (Network Access)
        """
        self.getJavaClass().setClass(value)

    def getSupplychainID(self) -> int:
        """!
        Maximum values are 99 for Barcode C and 999999 for Barcode L.
        @return:
        """
        return int(self.getJavaClass().getSupplychainID())

    def setSupplychainID(self, value: int) -> None:
        """!
        Maximum values are 99 for Barcode C and 999999 for Barcode L.
        @param: value:
        @return:
        """
        self.getJavaClass().setSupplychainID(value)

    def getItemID(self) -> int:
        """!
        Maximum value is 99999999.
        @return:
        """
        return int(self.getJavaClass().getItemID())

    def setItemID(self, value: int) -> None:
        """!
        Maximum value is 99999999.
        @param: value:
        @return:
        """
        self.getJavaClass().setItemID(value)

    def getDestinationPostCodePlusDPS(self) -> str:
        """!
        The PC and DP must comply with a PAF format.
        Nine character string denoting international "XY11     " (note the 5 trailing spaces) or a pattern
        of characters denoting a domestic sorting code.
        A domestic sorting code consists of an outward postcode, an inward postcode, and a Delivery Point Suffix.

        @return:
        """
        value = self.getJavaClass().getDestinationPostCodePlusDPS()
        return str(value) if value is not None else None

    def setDestinationPostCodePlusDPS(self, value: str) -> None:
        """!
        The PC and DP must comply with a PAF format.
        Nine character string denoting international "XY11     " (note the 5 trailing spaces) or a pattern
        of characters denoting a domestic sorting code.
        A domestic sorting code consists of an outward postcode, an inward postcode, and a Delivery Point Suffix.

        @param: value:
        @return:
        """
        self.getJavaClass().setDestinationPostCodePlusDPS(value)

    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Construct codetext from Mailmark data.
        @return: Constructed codetext
        """
        return str(self.getJavaClass().getConstructedCodetext())

    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes Mailmark data from constructed codetext.
        @param: constructedCodetext: Constructed codetext
        @return:
        """
        self.getJavaClass().initFromString(constructedCodetext)

    def getBarcodeType(self) -> Generation.EncodeTypes:
        """!
        Gets barcode type.
        @return: Barcode type.
        """
        return Generation.EncodeTypes(self.getJavaClass().getBarcodeType())

class Mailmark2DCodetext(IComplexCodetext):

    javaClassName = "com.aspose.mw.barcode.complexbarcode.MwMailmark2DCodetext"

    @staticmethod
    def construct(javaClass) -> Mailmark2DCodetext:
        jsClass = Mailmark2DCodetext()
        jsClass.setJavaClass(javaClass)
        return jsClass

    def getUPUCountryID(self) -> str:
        """!
        Identifies the UPU Country ID.Max length: 4 characters.
        @return Country ID
        """
        value = self.getJavaClass().getUPUCountryID()
        return str(value) if value is not None else None

    def setUPUCountryID(self, value: str) -> None:
        """!
            Identifies the UPU Country ID.Max length: 4 characters.
            @param value Country ID
        """
        self.getJavaClass().setUPUCountryID(value)

    def getInformationTypeID(self) -> str:
        """!
        Identifies the Royal Mail Mailmark barcode payload for each product type.
        Valid Values:

        “0” - Domestic Sorted &amp; Unsorted
        “A” - Online Postage
        “B” - Franking
        “C” - Consolidation

        @return Information type ID
        """
        value = self.getJavaClass().getInformationTypeID()
        return str(value) if value is not None else None

    def setInformationTypeID(self, value: str) -> None:
        """!
        Identifies the Royal Mail Mailmark barcode payload for each product type.
        Valid Values:

        “0” - Domestic Sorted &amp; Unsorted
        “A” - Online Postage
        “B” - Franking
        “C” - Consolidation

        @param value Information type ID
        """
        self.getJavaClass().setInformationTypeID(value)

    def getVersionID(self) -> str:
        """!
        Identifies the  barcode version as relevant to each Information Type ID.
        Valid Values:

        Currently “1”.
        “0” &amp; “2” to “9” and “A” to “Z” spare reserved for potential future use.

        @return Version ID
        """
        value = self.getJavaClass().getVersionID()
        return str(value) if value is not None else None

    def setVersionID(self, value: str) -> None:
        """!
        Identifies the  barcode version as relevant to each Information Type ID.
        Valid Values:

        Currently “1”.
        “0” &amp; “2” to “9” and “A” to “Z” spare reserved for potential future use.

        @param value Version ID
        """
        self.getJavaClass().setVersionID(value)

    def getClass_(self) -> str:
        """!
        Identifies the class of the item.

        Valid Values:
        “1” - 1C (Retail)
        “2” - 2C (Retail)
        “3” - Economy (Retail)
        “5” - Deffered (Retail)
        “8” - Premium (Network Access)
        “9” - Standard (Network Access)

        @return class of the item
        """
        value = self.getJavaClass().getClass_()
        return str(value) if value is not None else None

    def setClass_(self, value: str) -> None:
        """!
        Identifies the class of the item.
        @param value Valid Values:
        “1” - 1C (Retail)
        “2” - 2C (Retail)
        “3” - Economy (Retail)
        “5” - Deffered (Retail)
        “8” - Premium (Network Access)
        “9” - Standard (Network Access)
        @return: class of the item
        """
        self.getJavaClass().setclass(value)

    def getSupplyChainID(self) -> int:
        """!
        Identifies the unique group of customers involved in the mailing.
        Max value: 9999999.

        @return Supply chain ID
        """
        return int(self.getJavaClass().getSupplyChainID())

    def setSupplyChainID(self, value: int) -> None:
        """!
        Identifies the unique group of customers involved in the mailing.
        Max value: 9999999.
        @@param:: value: Supply chain ID
        """
        self.getJavaClass().setSupplyChainID(value)

    def getItemID(self) -> int:
        """!
        Every Mailmark barcode is required to carry an ID
        Max value: 99999999.

        @return: item within the Supply Chain ID
        """
        return int(self.getJavaClass().getItemID())

    def setItemID(self, value: int) -> None:
        """!
        Identifies the unique item within the Supply Chain ID.
        Every Mailmark barcode is required to carry an ID
        Max value: 99999999.
        """
        self.getJavaClass().setItemID(value)

    def getDestinationPostCodeAndDPS(self) -> str:
        """!
        Contains the Postcode of the Delivery Address with DPS
        If inland the Postcode/DP contains the following number of characters.
        Area (1 or 2 characters) District(1 or 2 characters)
        Sector(1 character) Unit(2 characters) DPS (2 characters).
        The Postcode and DPS must comply with a valid PAF® format.

        @return the Postcode of the Delivery Address with DPS
        """
        value = self.getJavaClass().getDestinationPostCodeAndDPS()
        return str(value) if value is not None else None

    def setDestinationPostCodeAndDPS(self, value: str) -> None:
        """!
        Contains the Postcode of the Delivery Address with DPS
        If inland the Postcode/DP contains the following number of characters.
        Area (1 or 2 characters) District(1 or 2 characters)
        Sector(1 character) Unit(2 characters) DPS (2 characters).
        The Postcode and DPS must comply with a valid PAF® format.
        @param: value: the Postcode of the Delivery Address with DPS
        """
        self.getJavaClass().setDestinationPostCodeAndDPS(value)

    def getRTSFlag(self) -> str:
        """!
        Flag which indicates what level of Return to Sender service is being requested.
        @return RTS Flag
        """
        value = self.getJavaClass().getRTSFlag()
        return str(value) if value is not None else None

    def setRTSFlag(self, value: str) -> None:
        """!
        Flag which indicates what level of Return to Sender service is being requested.
        @param: value: RTS Flag
        """
        self.getJavaClass().setRTSFlag(value)

    def getReturnToSenderPostCode(self) -> str:
        """!
        Contains the Return to Sender Post Code but no DPS.
        The PC(without DPS) must comply with a PAF® format.
        @return: Return to Sender Post Code but no DPS
        """
        value = self.getJavaClass().getReturnToSenderPostCode()
        return str(value) if value is not None else None

    def setReturnToSenderPostCode(self, value: str) -> None:
        """!
        Contains the Return to Sender Post Code but no DPS.
        The PC(without DPS) must comply with a PAF® format.
        @param: value: Return to Sender Post Code but no DPS
        """
        self.getJavaClass().setReturnToSenderPostCode(value)

    def getCustomerContent(self) -> str:
        """!
         Optional space for use by customer.

         Max length by Type:
         Type 7: 6 characters
         Type 9: 45 characters
         Type 29: 25 characters

        @return: Customer content
        """
        value = self.getJavaClass().getCustomerContent()
        return str(value) if value is not None else None

    def setCustomerContent(self, value: str) -> None:
        """!
        Optional space for use by customer.

        Max length by Type:
        Type 7: 6 characters
        Type 9: 45 characters
        Type 29: 25 characters

        @param value  Customer content
        """
        self.getJavaClass().setCustomerContent(value)

    def getCustomerContentEncodeMode(self) -> Generation.DataMatrixEncodeMode:
        """!
        Encode mode of Datamatrix barcode.
        Default value: DataMatrixEncodeMode.C40.

        @return Encode mode of Datamatrix barcode.
        """
        return Generation.DataMatrixEncodeMode(self.getJavaClass().getCustomerContentEncodeMode())

    def setCustomerContentEncodeMode(self, value: Generation.DataMatrixEncodeMode) -> None:
        """!
        Encode mode of Datamatrix barcode.
        Default value: DataMatrixEncodeMode.C40.
        @param: value: Encode mode of Datamatrix barcode.
        """
        self.getJavaClass().setCustomerContentEncodeMode(value.value)

    def getDataMatrixType(self) -> Mailmark2DType:
        """!
        2D Mailmark Type defines size of Data Matrix barcode.
        @return: Size of Data Matrix barcode
        """
        return Mailmark2DType(self.getJavaClass().getDataMatrixType())

    def setDataMatrixType(self, value: Mailmark2DType) -> None:
        """!
        2D Mailmark Type defines size of Data Matrix barcode.
        @param: value: Size of Data Matrix barcode
        """
        self.getJavaClass().setDataMatrixType(value.value)

    def __init__(self) -> None:
        """!
        Create default instance of Mailmark2DCodetext class.
        """
        javaMailmark2DCodetext = jpype.JClass(self.javaClassName)
        self.javaClass = javaMailmark2DCodetext()
        super().__init__(self.javaClass)
        self.init()

    def init(self) -> None:
        pass

    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Construct codetext from Mailmark data.
        @return: Constructed codetext
        """
        return str(self.getJavaClass().getConstructedCodetext())

    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes Mailmark data from constructed codetext.
        @param: constructedCodetext: constructedCodetext Constructed codetext.
        """
        str(self.getJavaClass().initFromString(constructedCodetext))

    def getBarcodeType(self) -> Generation.EncodeTypes:
        """!
        Gets barcode type.
        @return: Barcode type.
        """
        return Generation.EncodeTypes.DATA_MATRIX


class MaxiCodeCodetext(IComplexCodetext):
    """!
    Base class for encoding and decoding the text embedded in the MaxiCode code.

    This sample shows how to decode raw MaxiCode codetext to MaxiCodeCodetext instance.
    \code
      reader = Recognition.BarCodeReader(imagePath, None, Recognition.DecodeType.MAXI_CODE)
      for result in reader.readBarCodes():
          resultMaxiCodeCodetext = ComplexBarcode.ComplexCodetextReader.tryDecodeMaxiCode(
              result.getExtended().getMaxiCode().getMaxiCodeMode(), result.getCodeText())
          print("BarCode Type: " + str(resultMaxiCodeCodetext.getBarcodeType()))
          print("MaxiCode mode: " + str(resultMaxiCodeCodetext.getMode()))
    \endcode
    """
    @abstractmethod
    def getMode(self) -> Optional[Generation.MaxiCodeMode]:
        """!
        Gets MaxiCode mode.
        @return: MaxiCode mode or None if not set.
        """
        pass

    def getMaxiCodeEncodeMode(self) -> Generation.MaxiCodeEncodeMode:
        """!
        Gets a MaxiCode encode mode.
        """
        return Generation.MaxiCodeEncodeMode(int(self.getJavaClass().getMaxiCodeEncodeMode()))

    def setMaxiCodeEncodeMode(self, value: Generation.MaxiCodeEncodeMode) -> None:
        """!
        Sets a MaxiCode encode mode.
        """
        self.getJavaClass().setMaxiCodeEncodeMode(value.value)

    def getECIEncoding(self) -> Generation.ECIEncodings:
        """!
        Gets ECI encoding. Used when MaxiCodeEncodeMode is AUTO.
        """
        return Generation.ECIEncodings(self.getJavaClass().getECIEncoding())

    def setECIEncoding(self, eciEncodings: Generation.ECIEncodings) -> None:
        """!
        Sets ECI encoding. Used when MaxiCodeEncodeMode is AUTO.
        """
        self.getJavaClass().setECIEncoding(eciEncodings.value)

    def getBarcodeType(self) -> Generation.EncodeTypes:
        """!
        Gets barcode type.
        @return: Barcode type.
        """
        return Generation.EncodeTypes(self.getJavaClass().getBarcodeType())


class MaxiCodeSecondMessage(Assist.BaseJavaClass):
    """!
    Base class for encoding and decoding second message for MaxiCode barcode.
    """

    @abstractmethod
    def getMessage(self) -> Optional[str]:
        """!
        Gets constructed second message
        @return:  Constructed second message
        """
        pass


class MaxiCodeStandardCodetext(MaxiCodeCodetext):
    """!
    Class for encoding and decoding MaxiCode codetext for modes 4, 5 and 6.

    # Mode 4
      \code
         maxiCodeCodetext = MaxiCodeStandardCodetext()
         maxiCodeCodetext.setMode(MaxiCodeMode.MODE_4)
         maxiCodeCodetext.setMessage("Test message")
         complexGenerator = ComplexBarcodeGenerator(maxiCodeCodetext)
         complexGenerator.generateBarCodeImage()
      \endcode

      \code

           # Mode 5
           maxiCodeCodetext = MaxiCodeStandardCodetext()
           maxiCodeCodetext.setMode(MaxiCodeMode.MODE_5)
           maxiCodeCodetext.setMessage("Test message")
           complexGenerator = ComplexBarcodeGenerator(maxiCodeCodetext)
           complexGenerator.generateBarCodeImage()

      \endcode

      \code

           # Mode 6
           maxiCodeCodetext = MaxiCodeStandardCodetext()
           maxiCodeCodetext.setMode(MaxiCodeMode.MODE_6)
           maxiCodeCodetext.setMessage("Test message")
           complexGenerator = ComplexBarcodeGenerator(maxiCodeCodetext)
           complexGenerator.generateBarCodeImage()
      \endcode
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwMaxiCodeStandardCodetext"

    def __init__(self) -> None:
        try:
            java_class = jpype.JClass(MaxiCodeStandardCodetext.JAVA_CLASS_NAME)
            super().__init__(java_class())
        except Exception as ex:
            raise Assist.BarCodeException(ex)

    @staticmethod
    def construct(javaClass) -> MaxiCodeStandardCodetext:
        _class = MaxiCodeStandardCodetext()
        _class.setJavaClass(javaClass)
        return _class

    def getMessage(self) -> str:
        """!
        Gets message.
        """
        message = self.getJavaClass().getMessage()
        return str(message) if message is not None else None

    def setMessage(self, value: str) -> None:
        """!
        Sets message.
        """
        self.getJavaClass().setMessage(value)

    def setMode(self, mode: Generation.MaxiCodeMode) -> None:
        """!
        Sets MaxiCode mode. Standart codetext can be used only with modes 4, 5 and 6.
        """
        self.getJavaClass().setMode(mode.value)

    def getMode(self) -> Generation.MaxiCodeMode:
        """!
        Gets MaxiCode mode.
        @return:MaxiCode mode
        """
        return Generation.MaxiCodeMode(self.getJavaClass().getMode())

    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Constructs codetext
        @return:Constructed codetext
        """
        return str(self.getJavaClass().getConstructedCodetext())

    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes instance from constructed codetext.
        @param: constructedCodetext:Constructed codetext.
        """
        self.getJavaClass().initFromString(constructedCodetext)

    def __eq__(self, other: MaxiCodeStandardCodetext) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified MaxiCodeStandardCodetext value.
        @param: obj:An MaxiCodeStandardCodetext value to compare to this instance.
        @return: True if obj has the same value as this instance; otherwise, False.
        """
        if other is None:
            return False
        if not isinstance(other, MaxiCodeStandardCodetext):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def getHashCode(self) -> int:
        """!
        Returns the hash code for this instance.
        @return:A 32-bit signed integer hash code.
        """
        return int(self.getJavaClass().getHashCode())

    def init(self) -> None:
        pass


class MaxiCodeStandartSecondMessage(MaxiCodeSecondMessage):
    """!
    Class for encoding and decoding standart second message for MaxiCode barcode.
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwMaxiCodeStandartSecondMessage"

    def __init__(self) -> None:
        try:
            java_class = jpype.JClass(MaxiCodeStandartSecondMessage.JAVA_CLASS_NAME)
            super().__init__(java_class())
        except Exception as ex:
            raise Assist.BarCodeException(ex)

    @staticmethod
    def construct(javaClass) -> MaxiCodeStandartSecondMessage:
        _class = MaxiCodeStandartSecondMessage()
        _class.setJavaClass(javaClass)
        return _class

    def setMessage(self, value: str) -> None:
        """!
        Sets second message
        """
        self.getJavaClass().setMessage(value)

    def getMessage(self) -> str:
        """!
        Gets constructed second message
        @return:Constructed second message
        """
        value = self.getJavaClass().getMessage()
        return str(value) if value is not None else None

    def __eq__(self, other: MaxiCodeStandartSecondMessage) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified MaxiCodeStandartSecondMessage value.
        @param: obj:An MaxiCodeStandartSecondMessage value to compare to this instance.
        @return:True if obj has the same value as this instance; otherwise, False
        """
        if other is None:
            return False
        if not isinstance(other, MaxiCodeStandartSecondMessage):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def getHashCode(self) -> int:
        """!
        Returns the hash code for this instance.
        """
        return int(self.getJavaClass().getHashCode())

    def init(self) -> None:
        pass


class MaxiCodeStructuredCodetext(MaxiCodeCodetext):
    """!
    Base class for encoding and decoding the text embedded in the MaxiCode code for modes 2 and 3.

         This sample shows how to decode raw MaxiCode codetext to MaxiCodeStructuredCodetext instance.
         \code

         reader = Recognition.BarCodeReader(
             imagePath, None, DecodeType.MAXI_CODE)
         for result in reader.readBarCodes():
            resultMaxiCodeCodetext = ComplexCodetextReader.tryDecodeMaxiCode(
                result.getExtended().getMaxiCode().getMaxiCodeMode(), result.getCodeText())
            if resultMaxiCodeCodetext is MaxiCodeStructuredCodetext:
                maxiCodeStructuredCodetext = resultMaxiCodeCodetext
                print("BarCode Type: " + maxiCodeStructuredCodetext.getPostalCode())
                print("MaxiCode mode: " + \
                      maxiCodeStructuredCodetext.getCountryCode())
                print("BarCode CodeText: " + \
                      maxiCodeStructuredCodetext.getServiceCategory())
         \endcode
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwMaxiCodeStructuredCodetext"

    def __init__(self, javaClass) -> None:
        try:
            super().__init__(javaClass)
            self.maxiCodeSecondMessage: Optional[MaxiCodeSecondMessage] = None
        except Exception as ex:
            raise Assist.BarCodeException(ex)

    def init(self) -> None:
        javaMaxiCodeSecondMessage = self.getJavaClass().getSecondMessage()
        javaMaxiCodeStandartSecondMessageClass = jpype.JClass(MaxiCodeStandartSecondMessage.JAVA_CLASS_NAME)
        javaMaxiCodeStructuredSecondMessageClass = jpype.JClass(MaxiCodeStructuredSecondMessage.JAVA_CLASS_NAME)

        if javaMaxiCodeSecondMessage is None:
            self.maxiCodeSecondMessage = None
        elif str(javaMaxiCodeSecondMessage.getClass().toString()) == str(javaMaxiCodeStandartSecondMessageClass.class_.toString()):
             self.maxiCodeSecondMessage = MaxiCodeStandartSecondMessage.construct(javaMaxiCodeSecondMessage)
        elif str(javaMaxiCodeSecondMessage.getClass().toString()) == str(javaMaxiCodeStructuredSecondMessageClass.class_.toString()):
             self.maxiCodeSecondMessage = MaxiCodeStructuredSecondMessage.construct(javaMaxiCodeSecondMessage)
        else:
            raise Exception()

    def getPostalCode(self) -> str:
        """!
        Identifies the postal code. Must be 9 digits in mode 2 or
        6 alphanumeric symbols in mode 3.
        """
        value = self.getJavaClass().getPostalCode()
        return str(value) if value is not None else None

    def setPostalCode(self, value: str) -> None:
        """!
        Identifies the postal code. Must be 9 digits in mode 2 or
        6 alphanumeric symbols in mode 3.
        """
        self.getJavaClass().setPostalCode(value)

    def getCountryCode(self) -> int:
        """!
        Identifies 3 digit country code.
        """
        return int(self.getJavaClass().getCountryCode())

    def setCountryCode(self, value: int) -> None:
        """!
        Identifies 3 digit country code.
        """
        self.getJavaClass().setCountryCode(value)

    def getServiceCategory(self) -> int:
        """!
        Identifies 3 digit service category.
        """
        return int(self.getJavaClass().getServiceCategory())

    def setServiceCategory(self, value: int) -> None:
        """!
        Identifies 3 digit service category.
        """
        self.getJavaClass().setServiceCategory(value)

    def getSecondMessage(self) -> Optional[MaxiCodeSecondMessage]:
        """!
        Identifies second message of the barcode.
        """
        return self.maxiCodeSecondMessage

    def setSecondMessage(self, value: MaxiCodeSecondMessage) -> None:
        """!
        Identifies second message of the barcode.
        """
        self.maxiCodeSecondMessage = value
        self.getJavaClass().setSecondMessage(value.getJavaClass())

    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Constructs codetext
        @return:Constructed codetext
        """
        return str(self.getJavaClass().getConstructedCodetext())

    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes instance from constructed codetext.
        @param: constructedCodetext:Constructed codetext.
        """
        self.getJavaClass().initFromString(constructedCodetext)

    def __eq__(self, other: MaxiCodeStructuredCodetext) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified MaxiCodeStructuredCodetext value.
        @param: obj:An MaxiCodeStructuredCodetext value to compare to this instance.
        @return:True if obj has the same value as this instance; otherwise, False.
        """
        if other is None:
            return False
        if not isinstance(other, MaxiCodeStructuredCodetext):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def getHashCode(self) -> int:
        """!
        Returns the hash code for this instance.
        @return: A 32-bit signed integer hash code.
        """
        return int(self.getJavaClass().getHashCode())


class MaxiCodeCodetextMode2(MaxiCodeStructuredCodetext):
    """!
    Class for encoding and decoding the text embedded in the MaxiCode code for modes 2.

         This sample shows how to encode and decode MaxiCode codetext for mode 2.

         \code
         maxiCodeCodetext = MaxiCodeCodetextMode2()
         maxiCodeCodetext.setPostalCode("524032140")
         maxiCodeCodetext.setCountryCode(056)
         maxiCodeCodetext.setServiceCategory(999)
         maxiCodeStandartSecondMessage = MaxiCodeStandartSecondMessage()
         maxiCodeStandartSecondMessage.setMessage("Test message")
         maxiCodeCodetext.setSecondMessage(maxiCodeStandartSecondMessage)
         complexGenerator = ComplexBarcodeGenerator(maxiCodeCodetext)
         complexGenerator.generateBarCodeImage()

         \code
         \endcode

         maxiCodeCodetext = MaxiCodeCodetextMode2()
         maxiCodeCodetext.setPostalCode("524032140")
         maxiCodeCodetext.setCountryCode(056)
         maxiCodeCodetext.setServiceCategory(999)
         maxiCodeStructuredSecondMessage = MaxiCodeStructuredSecondMessage()
         maxiCodeStructuredSecondMessage.add("634 ALPHA DRIVE")
         maxiCodeStructuredSecondMessage.add("PITTSBURGH")
         maxiCodeStructuredSecondMessage.add("PA")
         maxiCodeStructuredSecondMessage.setYear(99)
         maxiCodeCodetext.setSecondMessage(maxiCodeStructuredSecondMessage)
         complexGenerator = ComplexBarcodeGenerator(maxiCodeCodetext)
         complexGenerator.generateBarCodeImage()

         \code
         \endcode

         reader = Recognition.BarCodeReader(imagePath, None, DecodeType.MAXI_CODE)
         for result in reader.readBarCodes():
            resultMaxiCodeCodetext = ComplexCodetextReader.tryDecodeMaxiCode(
                result.getExtended().getMaxiCode().getMaxiCodeMode(), result.getCodeText())
            if resultMaxiCodeCodetext is MaxiCodeCodetextMode2:
                maxiCodeStructuredCodetext = resultMaxiCodeCodetext
                print("BarCode Type: " + maxiCodeStructuredCodetext.getPostalCode())
                print("MaxiCode mode: " + maxiCodeStructuredCodetext.getCountryCode())
                print("BarCode CodeText: " + maxiCodeStructuredCodetext.getServiceCategory())
                if maxiCodeStructuredCodetext.SecondMessage is MaxiCodeStandartSecondMessage:
                    secondMessage = maxiCodeStructuredCodetext.getSecondMessage()
                    print("Message: " + secondMessage.getMessage())

         \code
         \endcode
        reader = Recognition.BarCodeReader(imagePath, None, DecodeType.MAXI_CODE)
        for result in reader.readBarCodes():
            resultMaxiCodeCodetext = ComplexCodetextReader.tryDecodeMaxiCode(
                result.getExtended().getMaxiCode().getMaxiCodeMode(), result.getCodeText())
            if resultMaxiCodeCodetext is MaxiCodeCodetextMode2:
                maxiCodeStructuredCodetext = resultMaxiCodeCodetext
                print("BarCode Type: " + maxiCodeStructuredCodetext.getPostalCode())
                print("MaxiCode mode: " + maxiCodeStructuredCodetext.getCountryCode())
                print("BarCode CodeText: " + maxiCodeStructuredCodetext.getServiceCategory())
                if maxiCodeStructuredCodetext.SecondMessage is MaxiCodeStructuredSecondMessage:
                    secondMessage = maxiCodeStructuredCodetext.getSecondMessage()
                    print("Message:")
                    for identifier in secondMessage.getIdentifiers():
                        print(identifier)
         \endcode
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwMaxiCodeCodetextMode2"

    def __init__(self) -> None:
        try:
            java_class = jpype.JClass(MaxiCodeCodetextMode2.JAVA_CLASS_NAME)
            super().__init__(java_class())
        except Exception as ex:
            raise Assist.BarCodeException(ex)

    @staticmethod
    def construct(javaClass) -> MaxiCodeCodetextMode2:
        _class = MaxiCodeCodetextMode2()
        _class.setJavaClass(javaClass)
        return _class

    def getMode(self) -> Optional[Generation.MaxiCodeMode]:
        """!
        Gets MaxiCode mode.
        @return:  MaxiCode mode or None if not set.
        """
        # return int(self.getJavaClass().getMode())
        mode_value = self.getJavaClass().getMode()
        if mode_value is None:
            return None
        return Generation.MaxiCodeMode(mode_value)

    def init(self) -> None:
        super().init()


class MaxiCodeCodetextMode3(MaxiCodeStructuredCodetext):
    """!
    Class for encoding and decoding the text embedded in the MaxiCode code for modes 3.
    This sample shows how to encode and decode MaxiCode codetext for mode 3.

     \code
     # Mode 3 with standart second message
     maxiCodeCodetext = MaxiCodeCodetextMode3()
     maxiCodeCodetext.setPostalCode("B1050")
     maxiCodeCodetext.setCountryCode(056)
     maxiCodeCodetext.setServiceCategory(999)
     maxiCodeStandartSecondMessage = MaxiCodeStandartSecondMessage()
     maxiCodeStandartSecondMessage.setMessage("Test message")
     maxiCodeCodetext.setSecondMessage(maxiCodeStandartSecondMessage)
     complexGenerator = ComplexBarcodeGenerator(maxiCodeCodetext)
     complexGenerator.generateBarCodeImage()

     \endcode
     \code

     # Mode 3 with structured second message
     maxiCodeCodetext = MaxiCodeCodetextMode3()
     maxiCodeCodetext.setPostalCode("B1050")
     maxiCodeCodetext.setCountryCode(156)
     maxiCodeCodetext.setServiceCategory(999)
     maxiCodeStructuredSecondMessage = MaxiCodeStructuredSecondMessage()
     maxiCodeStructuredSecondMessage.add("634 ALPHA DRIVE")
     maxiCodeStructuredSecondMessage.add("PITTSBURGH")
     maxiCodeStructuredSecondMessage.add("PA")
     maxiCodeStructuredSecondMessage.setYear(99)
     maxiCodeCodetext.setSecondMessage(maxiCodeStructuredSecondMessage)
     complexGenerator = ComplexBarcodeGenerator(maxiCodeCodetext)
     complexGenerator.generateBarCodeImage()

     \endcode
     \code
     # Decoding raw codetext with standart second message
    reader = Recognition.BarCodeReader(imagePath, None, DecodeType.MAXI_CODE)
    for result in reader.readBarCodes():
        resultMaxiCodeCodetext = ComplexCodetextReader.tryDecodeMaxiCode(
            result.getExtended().getMaxiCode().getMaxiCodeMode(), result.getCodeText())
        if resultMaxiCodeCodetext is MaxiCodeCodetextMode3:
            maxiCodeStructuredCodetext = resultMaxiCodeCodetext
            print("BarCode Type: " + maxiCodeStructuredCodetext.getPostalCode())
            print("MaxiCode mode: " + maxiCodeStructuredCodetext.getCountryCode())
            print("BarCode CodeText: " + maxiCodeStructuredCodetext.getServiceCategory())
            if maxiCodeStructuredCodetext.getSecondMessage() is MaxiCodeStandartSecondMessage:
                secondMessage = maxiCodeStructuredCodetext.getSecondMessage()
                print("Message: " + secondMessage.getMessage())
     \endcode
     \code
     reader = Recognition.BarCodeReader(imagePath, None, DecodeType.MAXI_CODE)
     for result in reader.readBarCodes():
        resultMaxiCodeCodetext = ComplexCodetextReader.tryDecodeMaxiCode(
            result.getExtended().getMaxiCode().getMaxiCodeMode(), result.getCodeText())
        if resultMaxiCodeCodetext is MaxiCodeCodetextMode3:
            maxiCodeStructuredCodetext = resultMaxiCodeCodetext
            print("BarCode Type: " + maxiCodeStructuredCodetext.getPostalCode())
            print("MaxiCode mode: " + maxiCodeStructuredCodetext.getCountryCode())
            print("BarCode CodeText: " + maxiCodeStructuredCodetext.getServiceCategory())
            if maxiCodeStructuredCodetext.getSecondMessage() is MaxiCodeStructuredSecondMessage:
                secondMessage = maxiCodeStructuredCodetext.getSecondMessage()
                print("Message:")
                for identifier in secondMessage.getIdentifiers():
                    print(identifier)
     \endcode
      """
    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwMaxiCodeCodetextMode3"

    def __init__(self) -> None:
        try:
            java_class = jpype.JClass(MaxiCodeCodetextMode3.JAVA_CLASS_NAME)
            super().__init__(java_class())
        except Exception as ex:
            raise Assist.BarCodeException(ex)

    @staticmethod
    def construct(javaClass) -> MaxiCodeCodetextMode3:
        _class = MaxiCodeCodetextMode3()
        _class.setJavaClass(javaClass)
        return _class

    def getMode(self) -> Optional[Generation.MaxiCodeMode]:
        """!
        Gets MaxiCode mode.
        @return:MaxiCode mode or None if not set.
        """
        # return int(self.getJavaClass().getMode())
        mode_value = self.getJavaClass().getMode()
        if mode_value is None:
            return None
        return Generation.MaxiCodeMode(mode_value)

    def init(self) -> None:
        super().init()


class MaxiCodeStructuredSecondMessage(MaxiCodeSecondMessage):
    """!
    Class for encoding and decoding structured second message for MaxiCode barcode.
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwMaxiCodeStructuredSecondMessage"

    def __init__(self) -> None:
        try:
            java_class = jpype.JClass(MaxiCodeStructuredSecondMessage.JAVA_CLASS_NAME)
            super().__init__(java_class())
            self.maxiCodeSecondMessage: Optional[MaxiCodeSecondMessage] = None
        except Exception as ex:
            raise Assist.BarCodeException(ex)

    @staticmethod
    def construct(javaClass) -> MaxiCodeStructuredSecondMessage:
        _class = MaxiCodeStructuredSecondMessage()
        _class.setJavaClass(javaClass)
        return _class

    def getYear(self) -> int:
        """!
        Gets year. Year must be 2 digit integer value.
        """
        return int(self.getJavaClass().getYear())

    def setYear(self, value: int) -> None:
        """!
        Sets year. Year must be 2 digit integer value.
        """
        self.getJavaClass().setYear(value)

    def getIdentifiers(self) -> List[str]:
        """!
        Gets identifiers list
        @return: List of identifiers
        """
        identifiers_string = self.getJavaClass().getIdentifiers()
        delimeter = "\\/\\"
        identifiers = identifiers_string.split(delimeter)
        return identifiers

    def add(self, identifier: str) -> None:
        """!
        Adds new identifier
        @param: identifier: Identifier to be added
        """
        self.getJavaClass().add(identifier)

    def clear(self) -> None:
        """!
        Clear identifiers list
        """
        self.getJavaClass().clear()

    def getMessage(self) -> str:
        """!
        Gets constructed second message
        @return: Constructed second message
        """
        value = self.getJavaClass().getMessage()
        return str(value) if value is not None else None

    def __eq__(self, other: MaxiCodeStructuredSecondMessage) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified MaxiCodeStructuredSecondMessage value.
        @param: obj: An MaxiCodeStructuredSecondMessage value to compare to this instance
        @return: <b>True</b> if obj has the same value as this instance; otherwise, <b>false</b>.
        """
        if other is None:
            return False
        if not isinstance(other, MaxiCodeStructuredSecondMessage):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def getHashCode(self) -> int:
        """!
        Returns the hash code for this instance.
        @return: A 32-bit signed integer hash code.
        """
        return int(self.getJavaClass().getHashCode())

    def init(self) -> None:
        pass


class HIBCLICComplexCodetext(IComplexCodetext):
    """!
    Base class for encoding and decoding the text embedded in the HIBC LIC code.

    This sample shows how to decode raw HIBC LIC codetext to HIBCLICComplexCodetext instance.
    \code
     reader = Recognition.BarCodeReader(imagePath, None, DecodeType.HIBC_AZTEC_LIC)
     for result in reader.readBarCodes():
         resultHIBCLICComplexCodetext = ComplexCodetextReader.tryDecodeHIBCLIC(result.getCodeText())
         print("BarCode Type: " + resultHIBCLICComplexCodetext.getBarcodeType())
         print("BarCode CodeText: " + resultHIBCLICComplexCodetext.getConstructedCodetext())
    \endcode
    """
    def __init__(self, javaClass) -> None:
        super().__init__(javaClass)

    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Constructs codetext
        @return:Constructed codetext
        """
        return None

    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes instance from constructed codetext.
        @param: constructedCodetext:Constructed codetext.
        """
        pass

    def getBarcodeType(self) -> Generation.EncodeTypes:
        """!
        Gets barcode type. HIBC LIC codetext can be encoded using HIBCCode39LIC, HIBCCode128LIC, HIBCAztecLIC, HIBCDataMatrixLIC and HIBCQRLIC encode types.
        Default value: HIBCCode39LIC.
        @return:Barcode type.
        """
        return Generation.EncodeTypes(self.getJavaClass().getBarcodeType())

    def setBarcodeType(self, value: Generation.EncodeTypes) -> None:
        """!
            Sets barcode type. HIBC LIC codetext can be encoded using HIBCCode39LIC, HIBCCode128LIC, HIBCAztecLIC, HIBCDataMatrixLIC and HIBCQRLIC encode types.
            Default value: HIBCCode39LIC.
            @return:Barcode type.
        """
        self.getJavaClass().setBarcodeType(value.value)


class HIBCLICCombinedCodetext(HIBCLICComplexCodetext):
    """!
      Class for encoding and decoding the text embedded in the HIBC LIC code which stores primary and secodary data.

      This sample shows how to encode and decode HIBC LIC using HIBCLICCombinedCodetext.
             \code
              combinedCodetext = HIBCLICCombinedCodetext()
              combinedCodetext.setBarcodeType(EncodeTypes.HIBCQRLIC)
              combinedCodetext.setPrimaryData(PrimaryData())
              combinedCodetext.getPrimaryData().setProductOrCatalogNumber("12345")
              combinedCodetext.getPrimaryData().setLabelerIdentificationCode("A999")
              combinedCodetext.getPrimaryData().setUnitOfMeasureID(1)
              combinedCodetext.setSecondaryAndAdditionalData(SecondaryAndAdditionalData())
              combinedCodetext.getSecondaryAndAdditionalData().setExpiryDate(datetime.now())
              combinedCodetext.getSecondaryAndAdditionalData().setExpiryDateFormat(HIBCLICDateFormat.MMDDYY)
              combinedCodetext.getSecondaryAndAdditionalData().setQuantity(30)
              combinedCodetext.getSecondaryAndAdditionalData().setLotNumber("LOT123")
              combinedCodetext.getSecondaryAndAdditionalData().setSerialNumber("SERIAL123")
              combinedCodetext.getSecondaryAndAdditionalData().setDateOfManufacture(datetime.now())
              generator = ComplexBarcode.ComplexBarcodeGenerator(combinedCodetext)
              image = generator.generateBarCodeImage()
              reader = Recognition.BarCodeReader(image, None, DecodeType.HIBCQRLIC)
              reader.readBarCodes()
              codetext = reader.getFoundBarCodes()[0].getCodeText()
              result = ComplexCodetextReader.tryDecodeHIBCLIC(codetext)
              if result is not None:
                  print("Product or catalog number: " + result.getPrimaryData().getProductOrCatalogNumber())
                  print("Labeler identification code: " + result.getPrimaryData().getLabelerIdentificationCode())
                  print("Unit of measure ID: " + result.getPrimaryData().getUnitOfMeasureID())
                  print("Expiry date: " + result.getSecondaryAndAdditionalData().getExpiryDate())
                  print("Quantity: " + result.getSecondaryAndAdditionalData().getQuantity())
                  print("Lot number: " + result.getSecondaryAndAdditionalData().getLotNumber())
                  print("Serial number: " + result.getSecondaryAndAdditionalData().getSerialNumber())
                  print("Date of manufacture: " + result.getSecondaryAndAdditionalData().getDateOfManufacture())
             \endcode
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwHIBCLICCombinedCodetext"

    def __init__(self) -> None:
        java_class_link = jpype.JClass(HIBCLICCombinedCodetext.JAVA_CLASS_NAME)
        javaClass = java_class_link()
        self.auto_PrimaryData: Optional[PrimaryData] = None
        self.auto_SecondaryAndAdditionalData: Optional[SecondaryAndAdditionalData] = None
        super().__init__(javaClass)

    @staticmethod
    def construct(javaClass) -> HIBCLICCombinedCodetext:
        obj = HIBCLICCombinedCodetext()
        obj.setJavaClass(javaClass)
        return obj

    def init(self) -> None:
        self.auto_PrimaryData = PrimaryData.construct(self.getJavaClass().getPrimaryData())
        self.auto_SecondaryAndAdditionalData = SecondaryAndAdditionalData.construct(
            self.getJavaClass().getSecondaryAndAdditionalData())

    def getPrimaryData(self) -> Optional[PrimaryData]:
        """!
        Identifies primary data.
        """
        return self.auto_PrimaryData

    def setPrimaryData(self, value: PrimaryData) -> None:
        """!
        Identifies primary data.
        """
        self.getJavaClass().setPrimaryData(value.getJavaClass())
        self.auto_PrimaryData = value

    def getSecondaryAndAdditionalData(self) -> Optional[SecondaryAndAdditionalData]:
        """!
        Identifies secondary and additional supplemental data.
        """
        return self.auto_SecondaryAndAdditionalData

    def setSecondaryAndAdditionalData(self, value: SecondaryAndAdditionalData) -> None:
        """!
        Identifies secondary and additional supplemental data.
        """
        self.getJavaClass().setSecondaryAndAdditionalData(value.getJavaClass())
        self.auto_SecondaryAndAdditionalData = value

    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Constructs codetext
        @return:Constructed codetext
        """
        return str(self.getJavaClass().getConstructedCodetext())

    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes instance from constructed codetext.
        @param: constructedCodetext:Constructed codetext.
        """
        self.getJavaClass().initFromString(constructedCodetext)

    def __eq__(self, other: HIBCLICCombinedCodetext) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified HIBCLICCombinedCodetext value.
            @param: obj:An  HIBCLICCombinedCodetext value to compare to this instance.
            @return: True if obj has the same value as this instance; otherwise,  False.
        """
        if other is None:
            return False
        if not isinstance(other, HIBCLICCombinedCodetext):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())


class HIBCLICPrimaryDataCodetext(HIBCLICComplexCodetext):
    """!
    Class for encoding and decoding the text embedded in the HIBC LIC code which stores primary data.

      This sample shows how to encode and decode HIBC LIC using HIBCLICPrimaryDataCodetext.
             \code
             complexCodetext = ComplexBarcode.HIBCLICPrimaryDataCodetext()
             complexCodetext.setBarcodeType(EncodeTypes.HIBCQRLIC)
             complexCodetext.setData(PrimaryData())
             complexCodetext.getData().setProductOrCatalogNumber("12345")
             complexCodetext.getData().setLabelerIdentificationCode("A999")
             complexCodetext.getData().setUnitOfMeasureID(1)
             generator = ComplexBarcode.ComplexBarcodeGenerator(complexCodetext)
             image = generator.generateBarCodeImage()
             reader = Recognition.BarCodeReader(image, None, DecodeType.HIBCQRLIC)
             reader.readBarCodes()
             codetext = reader.getFoundBarCodes()[0].getCodeText()
             result = ComplexBarcode.ComplexCodetextReader.tryDecodeHIBCLIC(codetext)
             print("Product or catalog number: " + result.getData().getProductOrCatalogNumber())
             print("Labeler identification code: " + result.getData().getLabelerIdentificationCode())
             print("Unit of measure ID: " + result.getData().getUnitOfMeasureID())
             \endcode
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwHIBCLICPrimaryDataCodetext"

    def __init__(self) -> None:
        java_class_link = jpype.JClass(HIBCLICPrimaryDataCodetext.JAVA_CLASS_NAME)
        javaClass = java_class_link()
        self.data: Optional[PrimaryData] = None
        super().__init__(javaClass)

    @staticmethod
    def construct(java_class) -> HIBCLICPrimaryDataCodetext:
        obj = HIBCLICPrimaryDataCodetext()
        obj.setJavaClass(java_class)
        return obj

    def init(self) -> None:
        self.data = PrimaryData.construct(self.getJavaClass().getData())

    def getData(self) -> Optional[PrimaryData]:
        """!
        Identifies primary data.
        """
        return self.data

    def setData(self, value: PrimaryData) -> None:
        """!
        Identifies primary data.
        """
        self.getJavaClass().setData(value.getJavaClass())
        self.data = value

    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Constructs codetext
        @return:Constructed codetext
        """
        return str(self.getJavaClass().getConstructedCodetext())

    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes instance from constructed codetext.
            @param: constructedCodetext:Constructed codetext.
        """
        self.getJavaClass().initFromString(constructedCodetext)

    def __eq__(self, other: HIBCLICPrimaryDataCodetext) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified HIBCLICPrimaryDataCodetext value.
            @param: obj:An  HIBCLICPrimaryDataCodetext value to compare to this instance.
            @return:<b>True</b> if obj has the same value as this instance; otherwise, <b>False</b>.
        """
        if other is None:
            return False
        if not isinstance(other, HIBCLICPrimaryDataCodetext):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())


class HIBCLICSecondaryAndAdditionalDataCodetext(HIBCLICComplexCodetext):
    """!
         Class for encoding and decoding the text embedded in the HIBC LIC code which stores seconday data.

         This sample shows how to encode and decode HIBC LIC using HIBCLICSecondaryAndAdditionalDataCodetext.

               \code
                    complexCodetext = HIBCLICSecondaryAndAdditionalDataCodetext()
                    complexCodetext.setBarcodeType(EncodeTypes.HIBCQRLIC)
                    complexCodetext.setLinkCharacter('L')
                    complexCodetext.setData(SecondaryAndAdditionalData())
                    complexCodetext.getData().setExpiryDate(datetime.now())
                    complexCodetext.getData().setExpiryDateFormat(HIBCLICDateFormat.MMDDYY)
                    complexCodetext.getData().setQuantity(30)
                    complexCodetext.getData().setLotNumber("LOT123")
                    complexCodetext.getData().setSerialNumber("SERIAL123")
                    complexCodetext.getData().setDateOfManufacture(datetime.now())
                    generator = ComplexBarcodeGenerator(complexCodetext)
                    image = generator.generateBarCodeImage()
                    reader = Recognition.BarCodeReader(image, None, DecodeType.HIBCQRLIC)
                    reader.readBarCodes()
                    codetext = reader.getFoundBarCodes()[0].getCodeText()
                    result = ComplexCodetextReader.tryDecodeHIBCLIC(codetext)
                    if result is not None:
                        print("Expiry date: " + result.getData().getExpiryDate())
                        print("Quantity: " + result.getData().getQuantity())
                        print("Lot number: " + result.getData().getLotNumber())
                        print("Serial number: " + result.getData().getSerialNumber())
                        print("Date of manufacture: " + result.getData().getDateOfManufacture())
               \endcode
      """
    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwHIBCLICSecondaryAndAdditionalDataCodetext"

    def __init__(self) -> None:
        java_class_link = jpype.JClass(HIBCLICSecondaryAndAdditionalDataCodetext.JAVA_CLASS_NAME)
        javaClass = java_class_link()
        self.data: Optional[SecondaryAndAdditionalData] = None
        super().__init__(javaClass)

    @staticmethod
    def construct(java_class) -> HIBCLICSecondaryAndAdditionalDataCodetext:
        obj = HIBCLICSecondaryAndAdditionalDataCodetext()
        obj.setJavaClass(java_class)
        return obj

    def getData(self) -> Optional[SecondaryAndAdditionalData]:
        """!
        Identifies secondary and additional supplemental data.
        """
        return self.data

    def setData(self, value: SecondaryAndAdditionalData) -> None:
        """!
        Identifies secondary and additional supplemental data.
        """
        self.getJavaClass().setData(value.getJavaClass())
        self.data = value

    def getLinkCharacter(self) -> str:
        """!
        Identifies link character.
        """
        value = self.getJavaClass().getLinkCharacter()
        return str(value) if value is not None else None

    def setLinkCharacter(self, value: str) -> None:
        """!
        Identifies link character.
        """
        self.getJavaClass().setLinkCharacter(value)

    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Constructs codetext.
        @return:Constructed codetext
        """
        return str(self.getJavaClass().getConstructedCodetext())

    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes instance from constructed codetext.
        @param: constructedCodetext:Constructed codetext.
        """
        self.getJavaClass().initFromString(constructedCodetext)
        self.init()

    def __eq__(self, other: HIBCLICSecondaryAndAdditionalDataCodetext) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified HIBCLICSecondaryAndAdditionalDataCodetext value.
            @param: obj:An HIBCLICSecondaryAndAdditionalDataCodetext value to compare to this instance.
            @return: True if obj has the same value as this instance; otherwise, False.
        """
        if other is None:
            return False
        if not isinstance(other, HIBCLICSecondaryAndAdditionalDataCodetext):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())

    def init(self) -> None:
        self.data = SecondaryAndAdditionalData.construct(self.getJavaClass().getData())


class HIBCPASCodetext(IComplexCodetext):
    """!
    Class for encoding and decoding the text embedded in the HIBC PAS code.
       This sample shows how to encode and decode HIBC PAS using HIBCPASCodetext.
        \code
        complexCodetext = ComplexBarcode.HIBCPASCodetext()
        complexCodetext.setDataLocation(ComplexBarcode.HIBCPASDataLocation.PATIENT)
        complexCodetext.addRecord(ComplexBarcode.HIBCPASDataType.LABELER_IDENTIFICATION_CODE, "A123")
        complexCodetext.addRecord(ComplexBarcode.HIBCPASDataType.MANUFACTURER_SERIAL_NUMBER, "SERIAL123")
        complexCodetext.setBarcodeType(EncodeTypes.HIBC_DATA_MATRIX_PAS)
        generator = ComplexBarcodeGenerator(complexCodetext)
        reader = Recognition.BarCodeReader(generator.generateBarCodeImage(), None, DecodeType.HIBC_DATA_MATRIX_PAS)
        reader.readBarCodes()
        codetext = reader.getFoundBarCodes()[0].getCodeText()
        if codetext is not None:
            readCodetext = ComplexCodetextReader.tryDecodeHIBCPAS(codetext)
            print("Data location: " + readCodetext.getDataLocation())
            print("Data type: " + readCodetext.getRecords()[0].getDataType())
            print("Data: " + readCodetext.getRecords()[0].getData())
            print("Data type: " + readCodetext.getRecords()[1].getDataType())
            print("Data: " + readCodetext.getRecords()[1].getData())
        \endcode
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwHIBCPASCodetext"

    def __init__(self) -> None:
        java_class_link = jpype.JClass(HIBCPASCodetext.JAVA_CLASS_NAME)
        javaClass = java_class_link()
        super().__init__(javaClass)

    @staticmethod
    def construct(javaClass) -> HIBCPASCodetext:
        obj = HIBCPASCodetext()
        obj.setJavaClass(javaClass)
        return obj

    def init(self):
        pass

    def setBarcodeType(self, value: Generation.EncodeTypes) -> None:
        """!
            Sets barcode type. HIBC PAS codetext can be encoded using HIBCCode39PAS, HIBCCode128PAS, HIBCAztec:PAS, HIBCDataMatrixPAS and HIBCQRPAS encode types.
            Default value: HIBCCode39PAS.
            @return:Barcode type.
        """
        self.getJavaClass().setBarcodeType(value.value)

    def getDataLocation(self) -> HIBCPASDataLocation:
        """!
        Identifies data location.
        """
        return HIBCPASDataLocation(self.getJavaClass().getDataLocation())

    def setDataLocation(self, value: HIBCPASDataLocation) -> None:
        """!
        Identifies data location.
        """
        self.getJavaClass().setDataLocation(value.value)

    def getRecords(self) -> List[HIBCPASRecord]:
        """!
            Gets records list
            @return:List of records
        """
        _array = []
        mwRecordsList = self.getJavaClass().getRecords()
        listSize = mwRecordsList.size()
        for i in range(listSize):
            mwhibcpasRecord = mwRecordsList.get(i)
            _array.append(HIBCPASRecord.construct(mwhibcpasRecord))
        return _array

    def addRecord(self, dataType: HIBCPASDataType, data: str) -> None:
        """!
            Adds new record
            @param: dataType:Type of data
            @param: data:Data string
        """
        self.getJavaClass().addRecord(dataType.value, data)

    def addHIBCPASRecord(self, record: HIBCPASRecord) -> None:
        """!
        Adds new record.
        """
        self.getJavaClass().addRecord(record.getJavaClass())

    def clear(self) -> None:
        """!
        Clears records list.
        """
        self.getJavaClass().clear()

    def getBarcodeType(self) -> Generation.EncodeTypes:
        """!
        Gets barcode type.
        @return: Barcode type.
        """
        return Generation.EncodeTypes(self.getJavaClass().getBarcodeType())

    def getConstructedCodetext(self) -> Optional[str]:
        """!
        Constructs codetext.
        @return:Constructed codetext.
        """
        return str(self.getJavaClass().getConstructedCodetext())

    def initFromString(self, constructedCodetext: str) -> None:
        """!
        Initializes instance from constructed codetext.
        @param: constructedCodetext:Constructed codetext.
        """
        self.getJavaClass().initFromString(constructedCodetext)

    def __eq__(self, other: HIBCPASCodetext) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified HIBCPASCodetext value.
            @param: obj:An HIBCPASCodetext value to compare to this instance.
            @return:True if obj has the same value as this instance; otherwise, False.
        """
        if other is None:
            return False
        if not isinstance(other, HIBCPASCodetext):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())


class HIBCPASRecord(Assist.BaseJavaClass):
    """!
    Class for storing HIBC PAS record.
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwHIBCPASRecord"

    def __init__(self, dataType: HIBCPASDataType, data: str) -> None:
        """!
        HIBCPASRecord constructor
        @param: dataType:Type of data.
        @param: data:Data string.
        """
        java_class_link = jpype.JClass(HIBCPASRecord.JAVA_CLASS_NAME)
        javaClass = java_class_link(dataType.value, data)
        super().__init__(javaClass)

    @staticmethod
    def construct(javaClass) -> HIBCPASRecord:
        obj = HIBCPASRecord(HIBCPASDataType.LABELER_IDENTIFICATION_CODE, "")
        obj.setJavaClass(javaClass)
        return obj

    def init(self):
        pass

    def getDataType(self) -> HIBCPASDataType:
        """!
        Identifies data type.
        """
        return HIBCPASDataType(self.getJavaClass().getDataType())

    def setDataType(self, value: HIBCPASDataType) -> None:
        """!
        Identifies data type.
        """
        self.getJavaClass().setDataType(value)

    def getData(self) -> str:
        """!
        Identifies data.
        """
        value = self.getJavaClass().getData()
        return str(value) if value is not None else None

    def setData(self, value: str) -> None:
        """!
        Identifies data.
        """
        self.getJavaClass().setData(value)

    def __eq__(self, other: HIBCPASRecord) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified HIBCPASDataType value.
        @param: obj:An HIBCPASDataType value to compare to this instance.
        @return: True if obj has the same value as this instance; otherwise, False.
        """
        if other is None:
            return False
        if not isinstance(other, HIBCPASRecord):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())


class PrimaryData(Assist.BaseJavaClass):
    """!
    Class for storing HIBC LIC primary data.
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwPrimaryData"

    def __init__(self) -> None:
        java_class_link = jpype.JClass(PrimaryData.JAVA_CLASS_NAME)
        javaClass = java_class_link()
        super().__init__(javaClass)

    @staticmethod
    def construct(java_class) -> PrimaryData:
        obj = PrimaryData()
        obj.setJavaClass(java_class)
        return obj

    def getLabelerIdentificationCode(self) -> str:
        """!
        Gets the identification date of the labeler identification code.
        Labeler identification code must be 4 symbols alphanumeric string, with first character always being alphabetic.
        """
        value = self.getJavaClass().getLabelerIdentificationCode()
        return str(value) if value is not None else None

    def setLabelerIdentificationCode(self, value: str) -> None:
        """!
        Sets the identification date for the labeler code.
        Labeler identification code must be 4 symbols alphanumeric string, with first character always being alphabetic.
        """
        self.getJavaClass().setLabelerIdentificationCode(value)

    def getProductOrCatalogNumber(self) -> str:
        """!
        Identifies product or catalog number.
        """
        value = self.getJavaClass().getProductOrCatalogNumber()
        return str(value) if value is not None else None

    def setProductOrCatalogNumber(self, value: str) -> None:
        """!
        Identifies product or catalog number.
        """
        self.getJavaClass().setProductOrCatalogNumber(value)

    def getUnitOfMeasureID(self) -> int:
        """!
        Identifies unit of measure ID.
        """
        return int(self.getJavaClass().getUnitOfMeasureID())

    def setUnitOfMeasureID(self, value: int) -> None:
        """!
        Identifies unit of measure ID.
        """
        self.getJavaClass().setUnitOfMeasureID(value)

    def __str__(self) -> str:
        """!
        Converts data to string format according HIBC LIC specification.
        @return:Formatted string.
        """
        value = self.getJavaClass().toString()
        return str(value) if value is not None else ""

    def parseFromString(self, primaryDataCodetext: str) -> None:
        """!
        Instantiates primary data from string format according HIBC LIC specification.
        @param: primaryDataCodetext:Formatted string.
        """
        self.getJavaClass().parseFromString(primaryDataCodetext)

    def __eq__(self, other: PrimaryData) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified PrimaryData value.
        @param: obj:An PrimaryData value to compare to this instance.
        @return: True if obj has the same value as this instance; otherwise,  False.
        """
        if other is None:
            return False
        if not isinstance(other, PrimaryData):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())

    def init(self):
        pass

class SecondaryAndAdditionalData(Assist.BaseJavaClass):
    """!
    Class for storing HIBC LIC secondary and additional data.
    """

    JAVA_CLASS_NAME = "com.aspose.mw.barcode.complexbarcode.MwSecondaryAndAdditionalData"

    def __init__(self) -> None:
        java_class_link = jpype.JClass(SecondaryAndAdditionalData.JAVA_CLASS_NAME)
        javaClass = java_class_link()
        super().__init__(javaClass)

    @staticmethod
    def construct(java_class) -> SecondaryAndAdditionalData:
        obj = SecondaryAndAdditionalData()
        obj.setJavaClass(java_class)
        return obj

    def getExpiryDateFormat(self) -> HIBCLICDateFormat:
        """!
        Identifies expiry date format.
        """
        return HIBCLICDateFormat(self.getJavaClass().getExpiryDateFormat())

    def setExpiryDateFormat(self, value: HIBCLICDateFormat) -> None:
        """!
        Identifies expiry date format.
        """
        self.getJavaClass().setExpiryDateFormat(value.value)

    def getExpiryDate(self) -> datetime:
        """!
            Identifies expiry date. Will be used if ExpiryDateFormat is not set to None.
        """
        return datetime.fromtimestamp(int(str(self.getJavaClass().getExpiryDate())), tz=timezone.utc)

    def setExpiryDate(self, value: datetime) -> None:
        """!
            Identifies expiry date. Will be used if ExpiryDateFormat is not set to None.
        """
        self.getJavaClass().setExpiryDate(str(int(calendar.timegm(value.timetuple()))))

    def getLotNumber(self) -> str:
        """!
            Identifies lot or batch number. Lot/batch number must be alphanumeric string with up to 18 sybmols length.
        """
        value = self.getJavaClass().getLotNumber()
        return str(value) if value is not None else None

    def setLotNumber(self, value: Optional[str]) -> None:
        """!
            Identifies lot or batch number. Lot/batch number must be alphanumeric string with up to 18 sybmols length.
        """
        if value is None:
            value = "null"
        self.getJavaClass().setLotNumber(value)

    def getSerialNumber(self) -> str:
        """!
            Identifies serial number. Serial number must be alphanumeric string up to 18 sybmols length.
        """
        value = self.getJavaClass().getSerialNumber()
        return str(value) if value is not None else None

    def setSerialNumber(self, value: Optional[str]) -> None:
        """!
            Identifies serial number. Serial number must be alphanumeric string up to 18 sybmols length.
        """
        if value is None:
            value = "null"
        self.getJavaClass().setSerialNumber(value)

    def getDateOfManufacture(self) -> datetime:
        """!
        Identifies date of manufacture.
            Date of manufacture can be set to DateTime.MinValue in order not to use this field.
            Default value: DateTime.MinValue
        """
        return datetime.fromtimestamp(int(str(self.getJavaClass().getDateOfManufacture())), tz=timezone.utc)

    def setDateOfManufacture(self, value: datetime) -> None:
        """!
        Identifies date of manufacture.
            Date of manufacture can be set to DateTime.MinValue in order not to use this field.
            Default value: DateTime.MinValue
        """
        self.getJavaClass().setDateOfManufacture(str(int(calendar.timegm(value.timetuple()))))

    def getQuantity(self) -> int:
        """!
        Identifies quantity, must be integer value from 0 to 500.
            Quantity can be set to -1 in order not to use this field.
            Default value: -1
        """
        return int(self.getJavaClass().getQuantity())

    def setQuantity(self, value: int) -> None:
        """!
        Identifies quantity, must be integer value from 0 to 500.
            Quantity can be set to -1 in order not to use this field.
            Default value: -1
        """
        self.getJavaClass().setQuantity(value)

    def __str__(self) -> str:
        """!
        Converts data to string format according HIBC LIC specification.
        @return:Formatted string.
        """
        value = self.getJavaClass().toString()
        return str(value) if value is not None else ""

    def parseFromString(self, secondaryDataCodetext: str) -> None:
        """!
        Instantiates secondary and additional supplemental data from string format according HIBC LIC specification.
            @param: secondaryDataCodetext:Formatted string.
        """
        self.getJavaClass().parseFromString(secondaryDataCodetext)

    def __eq__(self, other: SecondaryAndAdditionalData) -> bool:
        """!
        Returns a value indicating whether this instance is equal to a specified SecondaryAndAdditionalData value.
            @param: obj:An SecondaryAndAdditionalData value to compare to this instance.
            @return: True if obj has the same value as this instance; otherwise, False.
        """
        if other is None:
            return False
        if not isinstance(other, SecondaryAndAdditionalData):
            return NotImplemented
        return bool(self.getJavaClass().equals(other.getJavaClass()))

    def __hash__(self) -> int:
        """!
        Returns the hash code for the current instance.
        @return A hash code for the current object.
        """
        return int(self.getJavaClass().hashCode())

    def init(self):
        pass

class Mailmark2DType(Enum):
      """!
      2D Mailmark Type defines size of Data Matrix barcode
      """

      ## Auto determine
      AUTO = 0

      ## 24 x 24 modules
      TYPE_7 = 1

      ## 32 x 32 modules
      TYPE_9 = 2

      ## 16 x 48 modules
      TYPE_29 = 3

class HIBCLICDateFormat(Enum):
      """!
      Specifies the different types of date formats for HIBC LIC.
      """

      ## YYYYMMDD format. Will be encoded in additional supplemental data.
      YYYYMMDD = 0

      ## MMYY format.
      MMYY =  1

      ## MMDDYY format.
      MMDDYY = 2

      ## YYMMDD format.
      YYMMDD =  3

      ## YYMMDDHH format.
      YYMMDDHH = 4

      ## Julian date format.
      YYJJJ = 5

      ## Julian date format with hours.
      YYJJJHH = 6

      ## Do not encode expiry date.
      NONE = 7

class HIBCPASDataLocation(Enum):
      """!
      HIBC PAS data location types.
      """

      ## A - Patient
      PATIENT = 0

      ## B - Patient Care Record
      PATIENT_CARE_RECORD = 1

      ## C - Specimen Container
      SPECIMEN_CONTAINER = 2

      ## D - Direct Patient Image Item
      DIRECT_PATIENT_IMAGE_ITEM = 3
      """         
      """

      ## E - Business Record
      BUSINESS_RECORD = 4

      ## F - Medical Administration Record
      MEDICAL_ADMINISTRATION_RECORD = 5

      ## G - Library Reference Material
      LIBRARY_REFERENCE_MATERIAL = 6

      ## H - Devices and Materials
      DEVICES_AND_MATERIALS = 7

      ## I - Identification Card
      IDENTIFICATION_CARD = 8

      ## J - Product Container
      PRODUCT_CONTAINER = 9

      ## K - Asset data type
      ASSET = 10

      ## L - Surgical Instrument
      SURGICAL_INSTRUMENT = 11

      ## Z - User Defined
      USER_DEFINED = 25


class HIBCPASDataType(Enum):
      """!
      HIBC PAS record's data types.
      """
      ## A - Labeler Identification Code
      LABELER_IDENTIFICATION_CODE = 0

      ## B - Service Identification
      SERVICE_IDENTIFICATION = 1

      ## C - Patient Identification
      PATIENT_IDENTIFICATION = 2

      ## D - Specimen Identification
      SPECIMEN_IDENTIFICATION = 3

      ## E - Personnel Identification
      PERSONNEL_IDENTIFICATION = 4

      ## F - Administrable Product Identification
      ADMINISTRABLE_PRODUCT_IDENTIFICATION = 5

      ## G - Implantable Product Information
      IMPLANTABLE_PRODUCT_INFORMATION = 6

      ## H - Hospital Item Identification
      HOSPITAL_ITEM_IDENTIFICATION = 7

      ## I - Medical Procedure Identification
      MEDICAL_PROCEDURE_IDENTIFICATION = 8

      ## J - Reimbursement Category
      REIMBURSEMENT_CATEGORY = 9

      ## K - Blood Product Identification
      BLOOD_PRODUCT_IDENTIFICATION = 10

      ## L - Demographic Data
      DEMOGRAPHIC_DATA = 11

      ## M - DateTime in YYYDDDHHMMG format
      DATE_TIME = 12

      ## N - Asset Identification
      ASSET_IDENTIFICATION = 13

      ## O - Purchase Order Number
      PURCHASE_ORDER_NUMBER = 14

      ## P - Dietary Item Identification
      DIETARY_ITEM_IDENTIFICATION = 15

      ## Q - Manufacturer Serial Number
      MANUFACTURER_SERIAL_NUMBER = 16

      ## R - Library Materials Identification
      LIBRARY_MATERIALS_IDENTIFICATION = 17

      ## S - Business Control Number
      BUSINESS_CONTROL_NUMBER = 18

      ## T - Episode of Care Identification
      EPISODE_OF_CARE_IDENTIFICATION = 19

      ## U - Health Industry Number
      HEALTH_INDUSTRY_NUMBER = 20

      ## V - Patient Visit ID
      PATIENT_VISIT_ID = 21

      ## X - XML Document
      XML_DOCUMENT = 22

      ## Z - User Defined
      USER_DEFINED = 25