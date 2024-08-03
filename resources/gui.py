# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.0.0-0-g0efcecf)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class EmpireView
###########################################################################

class EmpireView ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Empire View", pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( -1,-1 ), wx.DefaultSize )

		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Bases", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		self.m_staticText1.SetFont( wx.Font( 16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer1.Add( self.m_staticText1, 0, wx.ALL|wx.EXPAND, 5 )

		bSizer15 = wx.BoxSizer( wx.HORIZONTAL )

		self.buttonCreateBase = wx.Button( self, wx.ID_ANY, u"New", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.buttonCreateBase.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_NEW, wx.ART_BUTTON ) )
		bSizer15.Add( self.buttonCreateBase, 0, wx.ALL, 5 )

		self.buttonEditBase = wx.Button( self, wx.ID_ANY, u"Edit", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer15.Add( self.buttonEditBase, 0, wx.ALL, 5 )

		self.buttonDeleteBase = wx.Button( self, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer15.Add( self.buttonDeleteBase, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer15, 0, wx.EXPAND, 5 )

		self.basesList = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL )
		self.basesList.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.basesList.SetMinSize( wx.Size( 120,120 ) )

		bSizer1.Add( self.basesList, 1, wx.ALIGN_TOP|wx.ALL|wx.EXPAND, 5 )


		bSizer9.Add( bSizer1, 1, wx.EXPAND, 5 )

		bSizer11 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Empire Flows", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )

		bSizer11.Add( self.m_staticText4, 0, wx.ALL, 5 )

		bSizer32 = wx.BoxSizer( wx.HORIZONTAL )

		self.checkBoxBalance = wx.CheckBox( self, wx.ID_ANY, u"Empire Balancing", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer32.Add( self.checkBoxBalance, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText44 = wx.StaticText( self, wx.ID_ANY, u"Fltr", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText44.Wrap( -1 )

		bSizer32.Add( self.m_staticText44, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrlFlowsFilter = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		bSizer32.Add( self.textCtrlFlowsFilter, 1, wx.ALL, 5 )


		bSizer11.Add( bSizer32, 0, wx.EXPAND, 5 )

		self.flowsList = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.flowsList.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer11.Add( self.flowsList, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer9.Add( bSizer11, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer9 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


###########################################################################
## Class BaseView
###########################################################################

class BaseView ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1440,900 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer12 = wx.BoxSizer( wx.VERTICAL )

		bSizer13 = wx.BoxSizer( wx.HORIZONTAL )

		self.labelBaseName = wx.StaticText( self, wx.ID_ANY, u"My Base", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelBaseName.Wrap( -1 )

		self.labelBaseName.SetFont( wx.Font( 16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer13.Add( self.labelBaseName, 0, wx.ALL, 5 )

		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		self.m_staticline1.SetMinSize( wx.Size( 1,-1 ) )

		bSizer13.Add( self.m_staticline1, 0, wx.ALL|wx.EXPAND, 5 )

		self.labelArea = wx.StaticText( self, wx.ID_ANY, u"Area: 500 (1)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelArea.Wrap( -1 )

		bSizer13.Add( self.labelArea, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer12.Add( bSizer13, 0, wx.EXPAND, 5 )

		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer15 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"Resources", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )

		bSizer15.Add( self.m_staticText10, 0, wx.ALL, 5 )

		self.listCtrlResources = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.listCtrlResources.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer15.Add( self.listCtrlResources, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"Infrastructure", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )

		bSizer15.Add( self.m_staticText11, 0, wx.ALL, 5 )

		fgSizer2 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer2.SetFlexibleDirection( wx.BOTH )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, u"HB1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )

		fgSizer2.Add( self.m_staticText12, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlHB1 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 99, 0 )
		fgSizer2.Add( self.spinCtrlHB1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText14 = wx.StaticText( self, wx.ID_ANY, u"HBB", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText14.Wrap( -1 )

		fgSizer2.Add( self.m_staticText14, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlHBB = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 99, 0 )
		fgSizer2.Add( self.spinCtrlHBB, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText17 = wx.StaticText( self, wx.ID_ANY, u"HB2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText17.Wrap( -1 )

		fgSizer2.Add( self.m_staticText17, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlHB2 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 99, 0 )
		fgSizer2.Add( self.spinCtrlHB2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText171 = wx.StaticText( self, wx.ID_ANY, u"HBC", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText171.Wrap( -1 )

		fgSizer2.Add( self.m_staticText171, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlHBC = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 99, 0 )
		fgSizer2.Add( self.spinCtrlHBC, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText1711 = wx.StaticText( self, wx.ID_ANY, u"HB3", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1711.Wrap( -1 )

		fgSizer2.Add( self.m_staticText1711, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlHB3 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 99, 0 )
		fgSizer2.Add( self.spinCtrlHB3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText17111 = wx.StaticText( self, wx.ID_ANY, u"HBM", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText17111.Wrap( -1 )

		fgSizer2.Add( self.m_staticText17111, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlHBM = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 99, 0 )
		fgSizer2.Add( self.spinCtrlHBM, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText171111 = wx.StaticText( self, wx.ID_ANY, u"HB4", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText171111.Wrap( -1 )

		fgSizer2.Add( self.m_staticText171111, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlHB4 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 99, 0 )
		fgSizer2.Add( self.spinCtrlHB4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText1711111 = wx.StaticText( self, wx.ID_ANY, u"HBL", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1711111.Wrap( -1 )

		fgSizer2.Add( self.m_staticText1711111, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlHBL = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 99, 0 )
		self.spinCtrlHBL.SetHelpText( u"https://i.imgur.com/BxtQyQK.png" )

		fgSizer2.Add( self.spinCtrlHBL, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText17111111 = wx.StaticText( self, wx.ID_ANY, u"HB5", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText17111111.Wrap( -1 )

		fgSizer2.Add( self.m_staticText17111111, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlHB5 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 99, 0 )
		self.spinCtrlHB5.SetHelpText( u"https://i.imgur.com/BxtQyQK.png" )

		fgSizer2.Add( self.spinCtrlHB5, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText171111111 = wx.StaticText( self, wx.ID_ANY, u"STO", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText171111111.Wrap( -1 )

		fgSizer2.Add( self.m_staticText171111111, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.spinCtrlSTO = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 99, 0 )
		self.spinCtrlSTO.SetHelpText( u"https://i.imgur.com/BxtQyQK.png" )

		fgSizer2.Add( self.spinCtrlSTO, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer15.Add( fgSizer2, 1, wx.EXPAND, 5 )

		self.m_staticText40 = wx.StaticText( self, wx.ID_ANY, u"Bonuses", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText40.Wrap( -1 )

		bSizer15.Add( self.m_staticText40, 0, wx.ALL, 5 )

		bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

		self.checkBoxCompanyHQ = wx.CheckBox( self, wx.ID_ANY, u"Your HQ", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer21.Add( self.checkBoxCompanyHQ, 0, wx.ALL, 5 )

		self.checkBoxCorpHQ = wx.CheckBox( self, wx.ID_ANY, u"Corp HQ", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer21.Add( self.checkBoxCorpHQ, 0, wx.ALL, 5 )


		bSizer15.Add( bSizer21, 0, wx.EXPAND, 5 )

		bSizer26 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText27 = wx.StaticText( self, wx.ID_ANY, u"COGC", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText27.Wrap( -1 )

		bSizer26.Add( self.m_staticText27, 0, wx.ALL, 5 )

		choiceCogcChoices = []
		self.choiceCogc = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceCogcChoices, 0 )
		self.choiceCogc.SetSelection( 0 )
		bSizer26.Add( self.choiceCogc, 1, wx.ALL, 5 )


		bSizer15.Add( bSizer26, 0, wx.EXPAND, 5 )

		fgSizer21 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer21.SetFlexibleDirection( wx.BOTH )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, u"Agri", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )

		fgSizer21.Add( self.m_staticText25, 0, wx.ALL, 5 )

		self.spinCtrlExpertsAGRICULTURE = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer21.Add( self.spinCtrlExpertsAGRICULTURE, 0, wx.ALL, 5 )

		self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, u"Chem", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )

		fgSizer21.Add( self.m_staticText26, 0, wx.ALL, 5 )

		self.spinCtrlExpertsCHEMISTRY = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer21.Add( self.spinCtrlExpertsCHEMISTRY, 0, wx.ALL, 5 )

		self.m_staticText28 = wx.StaticText( self, wx.ID_ANY, u"Cons", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText28.Wrap( -1 )

		fgSizer21.Add( self.m_staticText28, 0, wx.ALL, 5 )

		self.spinCtrlExpertsCONSTRUCTION = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer21.Add( self.spinCtrlExpertsCONSTRUCTION, 0, wx.ALL, 5 )

		self.m_staticText29 = wx.StaticText( self, wx.ID_ANY, u"Elec", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText29.Wrap( -1 )

		fgSizer21.Add( self.m_staticText29, 0, wx.ALL, 5 )

		self.spinCtrlExpertsELECTRONICS = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer21.Add( self.spinCtrlExpertsELECTRONICS, 0, wx.ALL, 5 )

		self.m_staticText30 = wx.StaticText( self, wx.ID_ANY, u"Food", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText30.Wrap( -1 )

		fgSizer21.Add( self.m_staticText30, 0, wx.ALL, 5 )

		self.spinCtrlExpertsFOOD_INDUSTRIES = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer21.Add( self.spinCtrlExpertsFOOD_INDUSTRIES, 0, wx.ALL, 5 )

		self.m_staticText31 = wx.StaticText( self, wx.ID_ANY, u"Fuel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText31.Wrap( -1 )

		fgSizer21.Add( self.m_staticText31, 0, wx.ALL, 5 )

		self.spinCtrlExpertsFUEL_REFINING = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer21.Add( self.spinCtrlExpertsFUEL_REFINING, 0, wx.ALL, 5 )

		self.m_staticText32 = wx.StaticText( self, wx.ID_ANY, u"Mfg", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText32.Wrap( -1 )

		fgSizer21.Add( self.m_staticText32, 0, wx.ALL, 5 )

		self.spinCtrlExpertsMANUFACTURING = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer21.Add( self.spinCtrlExpertsMANUFACTURING, 0, wx.ALL, 5 )

		self.m_staticText33 = wx.StaticText( self, wx.ID_ANY, u"Met", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText33.Wrap( -1 )

		fgSizer21.Add( self.m_staticText33, 0, wx.ALL, 5 )

		self.spinCtrlExpertsMETALLURGY = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer21.Add( self.spinCtrlExpertsMETALLURGY, 0, wx.ALL, 5 )

		self.m_staticText34 = wx.StaticText( self, wx.ID_ANY, u"ResE", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText34.Wrap( -1 )

		fgSizer21.Add( self.m_staticText34, 0, wx.ALL, 5 )

		self.spinCtrlExpertsRESOURCE_EXTRACTION = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 10, 0 )
		fgSizer21.Add( self.spinCtrlExpertsRESOURCE_EXTRACTION, 0, wx.ALL, 5 )


		bSizer15.Add( fgSizer21, 1, wx.EXPAND, 5 )


		bSizer14.Add( bSizer15, 0, wx.EXPAND, 5 )

		bSizer16 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Summary", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )

		bSizer16.Add( self.m_staticText9, 0, wx.ALL, 5 )

		bSizer20 = wx.BoxSizer( wx.HORIZONTAL )

		self.listCtrlWorkforce = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.listCtrlWorkforce.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer20.Add( self.listCtrlWorkforce, 1, wx.ALL|wx.EXPAND, 5 )

		self.listCtrlSummary = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.listCtrlSummary.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer20.Add( self.listCtrlSummary, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer16.Add( bSizer20, 0, 0, 5 )

		bSizer19 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Production Buildings", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )

		bSizer19.Add( self.m_staticText8, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer19.Add( ( 0, 0), 1, 0, 5 )

		choiceNewBuildingChoices = []
		self.choiceNewBuilding = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceNewBuildingChoices, 0 )
		self.choiceNewBuilding.SetSelection( 0 )
		bSizer19.Add( self.choiceNewBuilding, 0, wx.ALL, 5 )

		self.buttonAddBuilding = wx.Button( self, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonAddBuilding.Enable( False )

		bSizer19.Add( self.buttonAddBuilding, 0, wx.ALL, 5 )


		bSizer16.Add( bSizer19, 0, wx.EXPAND, 5 )

		self.scrolledWindowProduction = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.scrolledWindowProduction.SetScrollRate( 5, 5 )
		sizerProduction = wx.BoxSizer( wx.VERTICAL )


		self.scrolledWindowProduction.SetSizer( sizerProduction )
		self.scrolledWindowProduction.Layout()
		sizerProduction.Fit( self.scrolledWindowProduction )
		bSizer16.Add( self.scrolledWindowProduction, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer14.Add( bSizer16, 1, wx.EXPAND, 5 )

		bSizer17 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"Material Flows", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )

		bSizer17.Add( self.m_staticText7, 0, wx.ALL, 5 )

		self.listCtrlMaterialFlows = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.listCtrlMaterialFlows.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer17.Add( self.listCtrlMaterialFlows, 2, wx.ALL|wx.EXPAND, 5 )

		radioBoxCargoBayChoices = [ u"SCB", u"WCB", u"LCB", u"VCB" ]
		self.radioBoxCargoBay = wx.RadioBox( self, wx.ID_ANY, u"Cargo Bay", wx.DefaultPosition, wx.DefaultSize, radioBoxCargoBayChoices, 1, wx.RA_SPECIFY_ROWS )
		self.radioBoxCargoBay.SetSelection( 0 )
		bSizer17.Add( self.radioBoxCargoBay, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText35 = wx.StaticText( self, wx.ID_ANY, u"Shopping List", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText35.Wrap( -1 )

		bSizer17.Add( self.m_staticText35, 0, wx.ALL, 5 )

		self.listCtrlShopping = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.listCtrlShopping.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer17.Add( self.listCtrlShopping, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer14.Add( bSizer17, 0, wx.EXPAND, 5 )


		bSizer12.Add( bSizer14, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer12 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


###########################################################################
## Class PlanetSearchView
###########################################################################

class PlanetSearchView ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Planet Search", pos = wx.DefaultPosition, size = wx.Size( 1440,900 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer22 = wx.BoxSizer( wx.VERTICAL )

		bSizer23 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText36 = wx.StaticText( self, wx.ID_ANY, u"Name / ID", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText36.Wrap( -1 )

		bSizer23.Add( self.m_staticText36, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrlSearch = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		bSizer23.Add( self.textCtrlSearch, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText38 = wx.StaticText( self, wx.ID_ANY, u"Dist from Sys (opt.)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38.Wrap( -1 )

		bSizer23.Add( self.m_staticText38, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrlDistFrom = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		bSizer23.Add( self.textCtrlDistFrom, 1, wx.ALL|wx.EXPAND, 5 )

		self.buttonSearch = wx.Button( self, wx.ID_ANY, u"Search", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer23.Add( self.buttonSearch, 0, wx.ALL, 5 )


		bSizer22.Add( bSizer23, 0, wx.EXPAND, 5 )

		bSizer25 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText37 = wx.StaticText( self, wx.ID_ANY, u"Resource", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText37.Wrap( -1 )

		bSizer25.Add( self.m_staticText37, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrlResourceFilter = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.textCtrlResourceFilter.SetMinSize( wx.Size( 200,-1 ) )

		bSizer25.Add( self.textCtrlResourceFilter, 0, wx.ALL, 5 )

		self.m_staticText40 = wx.StaticText( self, wx.ID_ANY, u"CoGC", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText40.Wrap( -1 )

		bSizer25.Add( self.m_staticText40, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.textCtrlCOGCFilter = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		self.textCtrlCOGCFilter.SetMinSize( wx.Size( 200,-1 ) )

		bSizer25.Add( self.textCtrlCOGCFilter, 0, wx.ALL, 5 )


		bSizer22.Add( bSizer25, 0, wx.EXPAND, 5 )

		self.listCtrlResults = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.listCtrlResults.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer22.Add( self.listCtrlResults, 1, wx.ALL|wx.EXPAND, 5 )

		bSizer24 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer24.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.buttonCreate = wx.Button( self, wx.ID_ANY, u"Create", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer24.Add( self.buttonCreate, 0, wx.ALL, 5 )


		bSizer22.Add( bSizer24, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer22 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


###########################################################################
## Class LogisticsManagerFrame
###########################################################################

class LogisticsManagerFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Logistics Manager", pos = wx.DefaultPosition, size = wx.Size( 1440,900 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer26 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer27 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText41 = wx.StaticText( self, wx.ID_ANY, u"Routes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText41.Wrap( -1 )

		bSizer27.Add( self.m_staticText41, 0, wx.ALL, 5 )

		bSizer30 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_button10 = wx.Button( self, wx.ID_ANY, u"New Route", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer30.Add( self.m_button10, 0, wx.ALL, 5 )

		self.m_button11 = wx.Button( self, wx.ID_ANY, u"Delete Route", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer30.Add( self.m_button11, 0, wx.ALL, 5 )


		bSizer27.Add( bSizer30, 0, wx.EXPAND, 5 )

		self.m_listCtrl9 = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.m_listCtrl9.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer27.Add( self.m_listCtrl9, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer26.Add( bSizer27, 1, wx.EXPAND, 5 )

		bSizer28 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText42 = wx.StaticText( self, wx.ID_ANY, u"Bases / Exchanges", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText42.Wrap( -1 )

		bSizer28.Add( self.m_staticText42, 0, wx.ALL, 5 )

		self.m_listCtrl10 = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.m_listCtrl10.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer28.Add( self.m_listCtrl10, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer26.Add( bSizer28, 1, wx.EXPAND, 5 )

		bSizer29 = wx.BoxSizer( wx.VERTICAL )

		self.m_listCtrl11 = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		self.m_listCtrl11.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer29.Add( self.m_listCtrl11, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer26.Add( bSizer29, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer26 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


###########################################################################
## Class ProductionBuildingPanel
###########################################################################

class ProductionBuildingPanel ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer20 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer20.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer13 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer14 = wx.BoxSizer( wx.VERTICAL )

		self.labelTicker = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelTicker.Wrap( -1 )

		self.labelTicker.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		bSizer14.Add( self.labelTicker, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )

		self.spinCtrlCount = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 999, 0 )
		bSizer14.Add( self.spinCtrlCount, 0, wx.ALL, 5 )

		self.labelCountDelta = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelCountDelta.Wrap( -1 )

		self.labelCountDelta.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer14.Add( self.labelCountDelta, 0, wx.ALL, 5 )

		self.buttonRemove = wx.Button( self, wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.buttonRemove.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_DELETE, wx.ART_BUTTON ) )
		self.buttonRemove.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

		bSizer14.Add( self.buttonRemove, 0, wx.ALL, 5 )


		bSizer13.Add( bSizer14, 0, wx.EXPAND, 5 )

		self.panelRecipes = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		wSizer1 = wx.WrapSizer( wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS )

		self.panelAddRecipe = wx.Panel( self.panelRecipes, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_SUNKEN|wx.TAB_TRAVERSAL )
		bSizer17 = wx.BoxSizer( wx.VERTICAL )

		choiceAddRecipeChoices = []
		self.choiceAddRecipe = wx.Choice( self.panelAddRecipe, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceAddRecipeChoices, 0 )
		self.choiceAddRecipe.SetSelection( 0 )
		self.choiceAddRecipe.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer17.Add( self.choiceAddRecipe, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )

		self.buttonAddRecipe = wx.Button( self.panelAddRecipe, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.buttonAddRecipe, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


		self.panelAddRecipe.SetSizer( bSizer17 )
		self.panelAddRecipe.Layout()
		bSizer17.Fit( self.panelAddRecipe )
		wSizer1.Add( self.panelAddRecipe, 1, wx.EXPAND |wx.ALL, 5 )


		self.panelRecipes.SetSizer( wSizer1 )
		self.panelRecipes.Layout()
		wSizer1.Fit( self.panelRecipes )
		bSizer13.Add( self.panelRecipes, 1, wx.EXPAND |wx.ALL, 0 )


		bSizer20.Add( bSizer13, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer20 )
		self.Layout()
		bSizer20.Fit( self )

	def __del__( self ):
		pass


###########################################################################
## Class ProductionBuildingRecipePanel
###########################################################################

class ProductionBuildingRecipePanel ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.BORDER_SUNKEN|wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer22 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer19 = wx.BoxSizer( wx.VERTICAL )

		self.labelRecipe = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelRecipe.Wrap( -1 )

		self.labelRecipe.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer19.Add( self.labelRecipe, 0, wx.ALL|wx.EXPAND, 5 )

		self.labelEstimatedProfit = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelEstimatedProfit.Wrap( -1 )

		self.labelEstimatedProfit.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer19.Add( self.labelEstimatedProfit, 0, wx.ALL, 5 )

		self.spinCtrlCount = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,-1 ), wx.SP_ARROW_KEYS, 0, 999, 0 )
		bSizer19.Add( self.spinCtrlCount, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		self.buttonRemove = wx.Button( self, wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.buttonRemove, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


		bSizer22.Add( bSizer19, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer22 )
		self.Layout()
		bSizer22.Fit( self )

	def __del__( self ):
		pass


###########################################################################
## Class SplashFrame
###########################################################################

class SplashFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = 0|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer31 = wx.BoxSizer( wx.VERTICAL )


		bSizer31.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText42 = wx.StaticText( self, wx.ID_ANY, u"Bob's Discount™ Planner", wx.DefaultPosition, wx.Size( -1,48 ), wx.ALIGN_CENTER_HORIZONTAL )
		self.m_staticText42.Wrap( -1 )

		self.m_staticText42.SetFont( wx.Font( 24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer31.Add( self.m_staticText42, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		self.m_staticText43 = wx.StaticText( self, wx.ID_ANY, u"loading...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText43.Wrap( -1 )

		bSizer31.Add( self.m_staticText43, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


		bSizer31.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer31 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


