#! -*- coding: utf-8 -*-
from qgis import core

class GeneratorCustomForm(object):
    def __init__(self):
        super(GeneratorCustomForm, self).__init__()

    def get_form_template(self):
        return u'''<?xml version="1.0" encoding="UTF-8"?>
            <ui version="4.0">
            <class>Dialog</class>
            <widget class="QDialog" name="Dialog">
            <property name="windowTitle">
            <string>Dialog</string>
            </property>
            <layout class="QGridLayout" name="gridLayout">
            <item row="0" column="0">
                <widget class="QLabel" name="label">
                <property name="text">
                <string>Relatório de erros :</string>
                </property>
                </widget>
            </item>
            <item row="0" column="1">
                <widget class="QPushButton" name="logBtn">
                <property name="text">
                <string>&gt;&gt;&gt;</string>
                </property>
                <property name="autoDefault">
                <bool>false</bool>
                </property>
                </widget>
            </item>
            <item row="0" column="2" rowspan="15" colspan="4">
                <widget class="QFrame" name="logFrame">
                <property name="frameShape">
                <enum>QFrame::StyledPanel</enum>
                </property>
                <property name="frameShadow">
                <enum>QFrame::Raised</enum>
                </property>
                <layout class="QVBoxLayout" name="verticalLayout">
                <item>
                <widget class="QLabel" name="logLabel">
                </widget>
                </item>
                </layout>
                </widget>
            </item>
            {items}
            <item row="{row_btn}" column="0" colspan="2">
                <widget class="QDialogButtonBox" name="buttonBox">
                <property name="orientation">
                <enum>Qt::Horizontal</enum>
                </property>
                <property name="standardButtons">
                <set>QDialogButtonBox::Cancel|QDialogButtonBox::Ok</set>
                </property>
                </widget>
            </item>
            </layout>
            <zorder>buttonBox</zorder>
            <zorder>logFrame</zorder>
            <zorder>logBtn</zorder>
            <zorder>layoutWidget</zorder>
            </widget>
            <resources/>
            <connections>
            <connection>
            <sender>buttonBox</sender>
            <signal>accepted()</signal>
            <receiver>Dialog</receiver>
            <slot>accept()</slot>
            <hints>
                <hint type="sourcelabel">
                <x>248</x>
                <y>254</y>
                </hint>
                <hint type="destinationlabel">
                <x>157</x>
                <y>274</y>
                </hint>
            </hints>
            </connection>
            <connection>
            <sender>buttonBox</sender>
            <signal>rejected()</signal>
            <receiver>Dialog</receiver>
            <slot>reject()</slot>
            <hints>
                <hint type="sourcelabel">
                <x>316</x>
                <y>260</y>
                </hint>
                <hint type="destinationlabel">
                <x>286</x>
                <y>274</y>
                </hint>
            </hints>
            </connection>
            </connections>
            </ui>
            '''

    def get_le_template(self, field, alias, row, readOnly=''):
        return '''<item row="{row}" column="0">
                <widget class="QLabel" name="label_{field}">
                <property name="text">
                <string>{alias}</string>
                </property>
                </widget>
            </item>
            <item row="{row}" column="1">
                <widget class="QLineEdit" name="{field}">
                {readOnly}
                </widget>
            </item>
            '''.format(alias=alias, field=field, row=row, readOnly=readOnly)

    def get_cb_template(self, field, alias, row):
        return '''<item row="{row}" column="0">
                <widget class="QLabel" name="label_{field}">
                <property name="text">
                <string>{alias}</string>
                </property>
                </widget>
            </item>
            <item row="{row}" column="1">
                <widget class="QComboBox" name="{field}"/>
            </item>'''.format(alias=alias, field=field, row=row)

    

    def create_cb(self, field, alias, row):
        return self.get_cb_template(field, alias, row)

    def create_le(self, field, alias, row, setReadOnly=False):
        """  if setReadOnly:
            readOnly =u'''<property name="readOnly">
                            <bool>true</bool>
                        </property>'''
            return self.get_le_template(field, row, readOnly) 
        else: """
        return self.get_le_template(field, alias, row) 

    def create(self, formFile, layerData, fieldsSorted, vlayer):
        form = self.get_form_template()
        layerData = layerData['layer_fields']
        all_items = u""
        rowAttr = 1
        for idx in vlayer.fields().allAttributesList():
            field = vlayer.fields().field(idx).name()
            field_alias = vlayer.fields().field(idx).alias()
            if field in [u'id', u'controle_id', u'ultimo_usuario', u'data_modificacao']:
                all_items += self.create_le(field, field_alias, rowAttr, setReadOnly=True)
            elif field == u'tipo':
                if u'filter' in layerData:
                    field_custom_name = u'filter'
                    all_items += self.create_cb(field_custom_name, field_custom_name, rowAttr)
                    rowAttr+=1
                all_items += self.create_cb(field, field_alias, rowAttr)
            elif (field in layerData)  and layerData[field]:
                all_items += self.create_cb(field, field_alias, rowAttr)
            elif (field in layerData):
                all_items += self.create_le(field, field_alias, rowAttr)
            rowAttr+=1
        if vlayer.geometryType() == 1:
            field_custom_name = u'length_otf'
            all_items += self.create_le(field_custom_name, field_custom_name, rowAttr)            
        elif vlayer.geometryType() == 2:
            field_custom_name = u'area_otf'
            all_items += self.create_le(field_custom_name, field_custom_name, rowAttr)   
        form = form.format(items=unicode(all_items), row_btn=rowAttr+1)
        formFile.write(form)
        formFile.close()

    