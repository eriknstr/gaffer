##########################################################################
#  
#  Copyright (c) 2013, Image Engine Design Inc. All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#  
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#  
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#  
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  
##########################################################################

import unittest

import IECore

import Gaffer
import GafferTest

class BoxTest( unittest.TestCase ) :
		
	def testSerialisation( self ) :
	
		s = Gaffer.ScriptNode()
		
		s["b"] = Gaffer.Box()
		s["b"]["n1"] = GafferTest.AddNode()
		s["b"]["n2"] = GafferTest.AddNode()
		s["b"]["n2"]["op1"].setInput( s["b"]["n1"]["sum"] )
		
		s2 = Gaffer.ScriptNode()		
		s2.execute( s.serialise() )

		self.assert_( s2["b"]["n2"]["op1"].getInput().isSame( s2["b"]["n1"]["sum"] ) )
	
	def testCreate( self ) :
	
		s = Gaffer.ScriptNode()
		
		s["n1"] = GafferTest.AddNode()
		s["n2"] = GafferTest.AddNode()
		s["n3"] = GafferTest.AddNode()
		s["n4"] = GafferTest.AddNode()
		
		s["n2"]["op1"].setInput( s["n1"]["sum"] )
		s["n2"]["op2"].setInput( s["n1"]["sum"] )
		
		s["n3"]["op1"].setInput( s["n2"]["sum"] )
		
		s["n4"]["op1"].setInput( s["n3"]["sum"] )
		s["n4"]["op2"].setInput( s["n3"]["sum"] )
		
		def assertPreConditions() :
		
			self.assertTrue( "Box" not in s )
			
			self.assertTrue( s["n2"]["op1"].getInput().isSame( s["n1"]["sum"] ) )
			self.assertTrue( s["n2"]["op2"].getInput().isSame( s["n1"]["sum"] ) )
		
			self.assertTrue( s["n3"]["op1"].getInput().isSame( s["n2"]["sum"] ) )
			
			self.assertTrue( s["n4"]["op1"].getInput().isSame( s["n3"]["sum"] ) )
			self.assertTrue( s["n4"]["op2"].getInput().isSame( s["n3"]["sum"] ) )
		
		assertPreConditions()
			
		with Gaffer.UndoContext( s ) :
			b = Gaffer.Box.create( s, Gaffer.StandardSet( [ s["n2"], s["n3"] ] ) )
		
		def assertPostConditions() :
		
			self.assertTrue( isinstance( b, Gaffer.Box ) )
			self.assertTrue( b.parent().isSame( s ) )

			self.assertTrue( "n2" not in s )
			self.assertTrue( "n3" not in s )

			self.assertTrue( "n2" in b )
			self.assertTrue( "n3" in b )

			self.assertTrue( b["n3"]["op1"].getInput().isSame( b["n2"]["sum"] ) )

			self.assertTrue( b["n2"]["op1"].getInput().node().isSame( b ) )
			self.assertTrue( b["n2"]["op2"].getInput().node().isSame( b ) )

			self.assertTrue( b["n2"]["op1"].getInput().getInput().isSame( s["n1"]["sum"] ) )
			self.assertTrue( b["n2"]["op2"].getInput().getInput().isSame( s["n1"]["sum"] ) )
			self.assertTrue( b["n2"]["op1"].getInput().isSame( b["n2"]["op2"].getInput() ) )

			self.assertTrue( s["n4"]["op1"].getInput().node().isSame( b ) )
			self.assertTrue( s["n4"]["op2"].getInput().node().isSame( b ) )

			self.assertTrue( s["n4"]["op1"].getInput().isSame( s["n4"]["op2"].getInput() ) )
	
		assertPostConditions()
	
		s.undo()
		assertPreConditions()
	
		s.redo()
		assertPostConditions()
	
	def testCreateWithScriptSelection( self ) :
	
		s = Gaffer.ScriptNode()
		
		s["n1"] = GafferTest.AddNode()
		s["n2"] = GafferTest.AddNode()
		s["n3"] = GafferTest.AddNode()
		s["n4"] = GafferTest.AddNode()
		
		s["n2"]["op1"].setInput( s["n1"]["sum"] )
		s["n2"]["op2"].setInput( s["n1"]["sum"] )
		
		s["n3"]["op1"].setInput( s["n2"]["sum"] )
		
		s["n4"]["op1"].setInput( s["n3"]["sum"] )
		s["n4"]["op2"].setInput( s["n3"]["sum"] )

		s.selection().add( [ s["n2"], s["n3"] ] )

		b = Gaffer.Box.create( s, s.selection() )
	
	def testCreateWithScriptSelectionReversed( self ) :
	
		s = Gaffer.ScriptNode()
		
		s["n1"] = GafferTest.AddNode()
		s["n2"] = GafferTest.AddNode()
		s["n3"] = GafferTest.AddNode()
		s["n4"] = GafferTest.AddNode()
		
		s["n2"]["op1"].setInput( s["n1"]["sum"] )
		s["n2"]["op2"].setInput( s["n1"]["sum"] )
		
		s["n3"]["op1"].setInput( s["n2"]["sum"] )
		
		s["n4"]["op1"].setInput( s["n3"]["sum"] )
		s["n4"]["op2"].setInput( s["n3"]["sum"] )

		s.selection().add( [ s["n3"], s["n2"] ] )

		b = Gaffer.Box.create( s, s.selection() )
		
	def testCompute( self ) :
	
		s = Gaffer.ScriptNode()
		
		s["n1"] = GafferTest.AddNode()
		s["n2"] = GafferTest.AddNode()
		s["n3"] = GafferTest.AddNode()
		s["n4"] = GafferTest.AddNode()
		
		s["n2"]["op1"].setInput( s["n1"]["sum"] )
		s["n2"]["op2"].setInput( s["n1"]["sum"] )
		
		s["n3"]["op1"].setInput( s["n2"]["sum"] )
		
		s["n4"]["op1"].setInput( s["n3"]["sum"] )
		s["n4"]["op2"].setInput( s["n3"]["sum"] )
		
		s["n1"]["op1"].setValue( 2 )
		s["n3"]["op2"].setValue( 3 )
		
		self.assertEqual( s["n1"]["sum"].getValue(), 2 )
		self.assertEqual( s["n2"]["sum"].getValue(), 4 )
		self.assertEqual( s["n3"]["sum"].getValue(), 7 )
		self.assertEqual( s["n4"]["sum"].getValue(), 14 )
		
		b = Gaffer.Box.create( s, Gaffer.StandardSet( [ s["n2"], s["n3"] ] ) )
	
		self.assertEqual( s["n1"]["sum"].getValue(), 2 )
		self.assertEqual( s["Box"]["n2"]["sum"].getValue(), 4 )
		self.assertEqual( s["Box"]["n3"]["sum"].getValue(), 7 )
		self.assertEqual( s["n4"]["sum"].getValue(), 14 )
	
	def testCreateWithNodesWithInternalConnections( self ) :
	
		s = Gaffer.ScriptNode()
		
		s["n1"] = GafferTest.AddNode()
		s["n2"] = Gaffer.Node()
		s["n3"] = GafferTest.AddNode()
		
		s["n2"]["in"] = Gaffer.IntPlug()
		s["n2"]["out"] = Gaffer.IntPlug( direction = Gaffer.Plug.Direction.Out )
		s["n2"]["__in"] = Gaffer.IntPlug()
		s["n2"]["__out"] = Gaffer.IntPlug( direction = Gaffer.Plug.Direction.Out )
		
		
		s["n2"]["in"].setInput( s["n1"]["sum"] )
		s["n2"]["out"].setInput( s["n2"]["in"] ) # internal shortcut connection
		s["n2"]["__in"].setInput( s["n2"]["__out"] ) # internal input connection
		s["n3"]["op1"].setInput( s["n2"]["out"] )
		
		s.selection().add( s["n2"] )
		b = Gaffer.Box.create( s, s.selection() )
		
		self.assertEqual( len( b ), 3 ) # one child node, an in plug and an out plug
		
		self.assertTrue( b["n2"]["in"].getInput().isSame( b["in"] ) )
		self.assertTrue( b["in"].getInput().isSame( s["n1"]["sum"] ) )
		
		self.assertTrue( b["n2"]["out"].getInput().isSame( b["n2"]["in"] ) )
		self.assertTrue( s["n3"]["op1"].getInput().isSame( b["out"] ) )
		
if __name__ == "__main__":
	unittest.main()
	