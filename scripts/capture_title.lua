-- Cold boot, controller input and reset only. Never writes ROM/RAM/PPU.
local out=assert(os.getenv('JAJA_QA_OUT'))
local frame=0
local function save(name,data)
  local f=assert(io.open(out..'/'..name,'wb'));f:write(data);f:close()
end
local function dump(name,kind,first,size)
  local t={};for i=first,first+size-1 do t[#t+1]=string.char(emu.read(i,kind)) end
  save(name,table.concat(t))
end
local trace=assert(io.open(out..'/prg_reads.csv','wb'))
trace:write('frame,pc,address,prg_offset,value\n')
emu.addMemoryCallback(function(address,value)
  if frame<60 then
    local m=emu.convertAddress(address,emu.memType.nesMemory)
    trace:write(string.format('%d,%04X,%04X,%04X,%02X\n',frame,emu.getState()['cpu.pc'],address,m.address,value))
  end
end,emu.callbackType.read,0x316f,0x31e1,emu.cpuType.nes,emu.memType.nesPrgRom)
local menuTrace=assert(io.open(out..'/menu_reads.csv','wb'))
menuTrace:write('frame,pc,address,prg_offset,value\n')
emu.addMemoryCallback(function(address,value)
  if frame<60 then
    local m=emu.convertAddress(address,emu.memType.nesMemory)
    menuTrace:write(string.format('%d,%04X,%04X,%04X,%02X\n',frame,emu.getState()['cpu.pc'],address,m.address,value))
  end
end,emu.callbackType.read,0x2c1a,0x2c20,emu.cpuType.nes,emu.memType.nesPrgRom)
local captures={[60]=true,[120]=true,[240]=true,[360]=true,[480]=true,[600]=true,[720]=true,[840]=true,[900]=true,[960]=true,[1020]=true,[1140]=true}
emu.addEventCallback(function()
  frame=frame+1
  if captures[frame] then
    local tag=string.format('frame_%04d',frame)
    save(tag..'.png',emu.takeScreenshot())
    dump(tag..'_ppu.bin',emu.memType.nesPpuDebug,0,0x4000)
    dump(tag..'_oam.bin',emu.memType.nesSpriteRam,0,256)
    dump(tag..'_ram.bin',emu.memType.nesMemory,0,0x800)
    local rows={};for k,v in pairs(emu.getState()) do rows[#rows+1]=tostring(k)..'='..tostring(v) end
    table.sort(rows);save(tag..'_state.txt',table.concat(rows,'\n'))
    local maps={};for a=0,0x1fff,0x400 do
      local m=emu.convertAddress(a,emu.memType.nesPpuMemory)
      maps[#maps+1]=string.format('%04X %s %s',a,tostring(m.address),tostring(m.memType))
    end
    save(tag..'_chr_mapping.txt',table.concat(maps,'\n'))
  end
  if frame==720 then emu.reset() end
  if frame==1140 then trace:close();menuTrace:close();emu.stop(0) end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
  emu.setInput({start=(frame>=240 and frame<248) or (frame>=960 and frame<968),select=frame>=900 and frame<908,a=frame>=360 and frame<600 and frame%60<8,b=false,up=false,down=false,left=frame>=360 and frame<420,right=frame>=420 and frame<600},0)
end,emu.eventType.inputPolled)
