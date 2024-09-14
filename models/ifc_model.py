# models/ifc_model.py

import ifcopenshell

class IFCModel:
    def __init__(self, filename):
        self.model = ifcopenshell.open(filename)

    def get_elements(self):
        return self.model.by_type('IfcProduct')

    def save(self, filename):
        self.model.write(filename)

    def modify_element_geometry(self, element_id, new_geometry):
        element = self.model.by_guid(element_id)
        if element:
            element.Representation = new_geometry
        else:
            print("Element not found")

    def modify_element_property(self, element_id, property_name, new_value):
        element = self.model.by_guid(element_id)
        if element:
            for definition in element.IsDefinedBy:
                if definition.RelatingPropertyDefinition.is_a('IfcPropertySet'):
                    for prop in definition.RelatingPropertyDefinition.HasProperties:
                        if prop.Name == property_name:
                            prop.NominalValue = new_value
        else:
            print("Element not found")
