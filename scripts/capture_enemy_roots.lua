-- Renderer coverage: force only A at native enemy-label entry $8751.
-- This is a controlled UI probe, not natural progression to all seven enemies.
local out=assert(os.getenv('JAJA_ENEMY_OUT'))
local frame=0;local localFrame=0;local root=0;local injected=false;local drawn=nil
local function save(name,data)
 local f=assert(io.open(out..'/'..name,'wb'));f:write(data);f:close()
end
local function dump(name,kind,first,size)
 local t={};for i=first,first+size-1 do t[#t+1]=string.char(emu.read(i,kind)) end
 save(name,table.concat(t))
end
local events=assert(io.open(out..'/events.csv','wb'));events:write('frame,local_frame,root,event,old_a,new_a\n')
local reads=assert(io.open(out..'/name_reads.csv','wb'));reads:write('frame,root,pc,file_offset,value\n')
emu.addMemoryCallback(function()
 if injected then return end
 local s=emu.getState();events:write(string.format('%d,%d,%d,inject_A,%d,%d\n',frame,localFrame,root,s['cpu.a'],root))
 emu.setState({['cpu.a']=root});injected=true
end,emu.callbackType.exec,0x8751,0x8751,emu.cpuType.nes)
emu.addMemoryCallback(function()
 if injected and drawn==nil then drawn=frame;events:write(string.format('%d,%d,%d,draw_complete,,\n',frame,localFrame,root)) end
end,emu.callbackType.exec,0x8798,0x8798,emu.cpuType.nes)
emu.addMemoryCallback(function(address,value)
 if not injected then return end
 local s=emu.getState();if s['cpu.pc']~=0x87b0 then return end
 local m=emu.convertAddress(address,emu.memType.nesMemory)
 reads:write(string.format('%d,%d,%04X,%04X,%02X\n',frame,root,s['cpu.pc'],m.address+16,value))
end,emu.callbackType.read,0x7a9,0x831,emu.cpuType.nes,emu.memType.nesPrgRom)
local function capture(suffix)
 local tag=string.format('root_%d_%s',root,suffix);save(tag..'.png',emu.takeScreenshot())
 dump(tag..'_ppu.bin',emu.memType.nesPpuDebug,0,0x4000)
 dump(tag..'_ram.bin',emu.memType.nesMemory,0,0x800)
 dump(tag..'_oam.bin',emu.memType.nesSpriteRam,0,256)
 local rows={};for k,v in pairs(emu.getState()) do rows[#rows+1]=tostring(k)..'='..tostring(v) end
 table.sort(rows);save(tag..'_state.txt',table.concat(rows,'\n'))
end
emu.addEventCallback(function()
 frame=frame+1;localFrame=localFrame+1
 if drawn and frame==drawn+30 then capture('label') end
 if drawn and frame==drawn+120 then capture('after') end
 if drawn and frame==drawn+150 then
  if root==6 then events:close();reads:close();emu.stop(0)
  else root=root+1;injected=false;drawn=nil;localFrame=0;emu.reset() end
 end
 if localFrame>1500 then events:close();reads:close();emu.stop(2) end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
 emu.setInput({start=localFrame>=240 and localFrame<248,select=false,a=false,b=false,up=false,down=false,left=false,right=false},0)
end,emu.eventType.inputPolled)
