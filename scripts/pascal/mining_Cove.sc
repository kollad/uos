program Mining;

const
  HomeX = 2459;
  HomeY = 898;
  
  Forge = $4006F085;
  Storage = $4009DD1B;         
  IngotsStorage = $4003EC5A;
  IngotsType = $1BF2;
  
  IronColor = $0000;
  IronCount = $20;
  
  WaitTime = 1000;
  WaitCycles = 7;
  LagWait = 15000;
  
var
  Terminated: Boolean;
  OreTypes: array of Word;
  MiningTypes: array of Word;
  //GemTypes: array of Word;
  MiningTool: Cardinal;

  
function CheckMiningTool: Boolean;
var
  CurTool: Integer;
  Tool: Cardinal;
begin
  CheckLag(LagWait);
  for CurTool := 0 to Length(MiningTypes) -1 do begin
     Tool := MiningTypes[CurTool];
     FindType(Tool, Backpack);
     MiningTool := FindItem;
     break;
  end;
  Result := FindCount > 0;
end;

procedure SmellOre;
var
  CurOre, CurIndex: Integer;
  CurItem: Cardinal;
  List: TStringList;
begin
  try
    List := TStringList.Create;
    for CurOre := 0 to Length(OreTypes) - 1 do begin
      if Dead or not Connected then Exit;
      CheckLag(LagWait);
      FindType(OreTypes[CurOre], Backpack);
      List.Clear;
      if GetFindedList(List) then begin
        CurIndex := 0;
        while CurIndex < List.Count do begin
          if Dead or not Connected then Exit;
          CurItem := StrToInt('$' + List.Strings[CurIndex]);
          CheckLag(LagWait);
          if (GetType(CurItem) <> OreTypes[CurOre])
            or (GetQuantity(CurItem) < 2) then begin
            Inc(CurIndex);
          end else begin
            if TargetPresent then CancelTarget;
            UseObject(CurItem);
            CheckLag(LagWait);
            WaitForTarget(WaitTime * 5);
            if TargetPresent then begin
              TargetToObject(Forge);
              CheckLag(LagWait);
              Wait(WaitTime);
            end;
            CheckLag(LagWait);
          end;
        end;
      end;
    end;
  finally
    List.Free;
  end;
end;

procedure DropOre;
var 
  List: TStringList;
  CurItem: Cardinal;
  CurOre, CurIndex: Integer;
  StartCount, ToMove: Integer;
begin
try
  AddToSystemJournal('Dropping ore');
    List := TStringList.Create;
    for CurOre := 0 to Length(OreTypes) - 1 do begin
      if Dead or not Connected then Exit;
      CheckLag(LagWait);
      FindType(OreTypes[CurOre], BackPack);
      List.Clear;  
      if GetFindedList(List) then begin
        CurIndex := 0;
        while CurIndex < List.Count do begin
          if Dead or not Connected then Exit;
          CurItem := StrToInt('$' + List.Strings[CurIndex]);
          CheckLag(LagWait);
          StartCount := GetQuantity(CurItem);
          ToMove := StartCount;
          if ToMove > 0 then begin
            if MoveItem(CurItem, ToMove, Storage, $FFFF, $FFFF, 0) then begin
              Inc(CurIndex);
              CurItem := CurItem + (StartCount - ToMove);
              CheckLag(LagWait);
              Wait(WaitTime);
          end;
          end else begin
            Inc(CurIndex);
            CurItem := CurItem + StartCount;
        end;
      end;
    end;   
  end;
  finally
    List.Free; 
    AddToSystemJournal('Dropped ore');
  end;
end;


procedure MoveIngots;
var
  List: TStringList;
  CurIndex: Integer;
  CurIngot: Cardinal;
  CurIron: Cardinal;
  StartCount, ToMove: Integer;
begin
  CheckLag(LagWait);
  FindType(IngotsType, BackPack);
  CurIron := 0;
  try
    List := TStringList.Create;
    if GetFindedList(List) then begin
      CurIndex := 0;
      while CurIndex < FindCount do begin
        if Dead or not Connected then Exit;
        CurIngot := StrToInt('$' + List.Strings[CurIndex]);
        CheckLag(LagWait);
        StartCount := GetQuantity(CurIngot);
        if (GetColor(CurIngot) = IronColor)
          and (CurIron < IronCount) then begin
          ToMove := StartCount - (IronCount - CurIron);
        end else begin
          ToMove := StartCount;
        end;
        if ToMove > 0 then begin
          if MoveItem(CurIngot, ToMove, IngotsStorage, $FFFF, $FFFF, 0) then begin
            Inc(CurIndex);
            CurIron := CurIron + (StartCount - ToMove);
            CheckLag(LagWait);
            Wait(WaitTime);
          end;
        end else begin
          Inc(CurIndex);
          CurIron := CurIron + StartCount;
        end;
      end;
    end;
  finally
    List.Free;
  end;
end;

function Go(X, Y: Integer): Boolean;
var
  InPlace: Boolean;
begin
  InPlace := False;   
       
  while not InPlace do begin
    if Dead or not Connected then Exit;
    Wait(WaitTime);
    MoveThroughNPC := 0;
    
    InPlace := NewMoveXY(X, Y, True, 0, False);  
    Result := InPlace;  
  end;
end;

function GoBase: Boolean;
begin
  AddToSystemJournal('Going home...');
  Result := Go(HomeX, HomeY);
  AddToSystemJournal('At home!');
end;

procedure CheckState;
begin
  if 1600 < Weight + 60 then begin
    while True do begin
      if Dead or not Connected then Exit;
      if GoBase() then Break;
      if GoBase() then Break;
    end;
             
    DropOre;
    Exit;
    //SmellOre;
    //MoveIngots;
    
    while True do begin
      if Dead or not Connected then Exit;
      if GoBase() then Continue;
    end;
  end;
  while not CheckMiningTool do begin
    if Dead or not Connected then Exit;
  end;
end;


procedure Mine(X, Y: Integer; PosX, PosY: Integer);
var
  StaticData: TStaticCell;
  Tile: Word;
  Z: ShortInt;
  Finded, Iron, Empty: Boolean; 
  //Counter: Byte;
  StartTime: TDateTime;
  i: Integer;
  idleCount: Integer;
begin
  Finded := False; 
  Iron := False;
  
  StaticData := ReadStaticsXY(X, Y, WorldNum);
  for i := 0 to StaticData.StaticCount - 1 do begin
    if i >= StaticData.StaticCount then Break;
    if (GetTileFlags(2, StaticData.Statics[i].Tile) and $200) = $200 then begin
      Tile := StaticData.Statics[i].Tile;
      Z := StaticData.Statics[i].Z;
      Finded := True;
      Break;
    end; 
  end;
  
  CheckState();
   
  while Finded do begin
    if Dead or not Connected then Exit;
    if TargetPresent then CancelTarget;
        while not CheckMiningTool do begin
          if Dead or not Connected then Exit;
          //CreateMiningTools;
        end;   
                     
        Empty := False;  
                         
        while not Empty do begin        
          Wait(WaitTime);
          UseObject(MiningTool);
          CheckLag(LagWait);
          WaitForTarget(WaitTime);
          if TargetPresent then begin  
            if Not (PosX = GetX(Self))
              or Not (PosY = GetY(Self))
                then begin Go(PosX, PosY); end; 
                
            StartTime := Now;    
            TargetToTile(Tile, X, Y, Z);          
            Finded := False;
            
            idleCount := 0;

            while Not Finded do begin
              CheckLag(LagWait);    
                 
              if idleCount >= 15 then begin
                Finded := True;
              end;

              if InJournalBetweenTimes('Try mining elsewhere|You cannot mine|nothing here to mine|Iron Ore|Copper Ore|Bronze Ore', StartTime, Now) > 0 then begin
                Empty := True;
                Finded := True;
              end; 
                                
              if InJournalBetweenTimes('You put|You loosen some rocks', StartTime, Now) > 0 then begin
                Finded := True;
              end;
              
              if Not Finded then Wait(WaitTime);

              idleCount := idleCount + 1;

            end;                
          end;
        end; 
        CheckState();              
        Exit;   
  end;                             
end;

procedure MinePoint(PosX, PosY: Integer);
var
  X, Y: Integer;
begin 

  if Not (PosX = GetX(Self)) or Not (PosY = GetY(Self)) then begin
    AddToSystemJournal('Moving to target location');
    Go(PosX, PosY); 
  end;
                           
  AddToSystemJournal('---At mining location---'); 
  AddToSystemJournal('Starting mining');    
                             
  X := GetX(Self);
  Y := GetY(Self);   
  
  Mine(X + 1, Y, PosX, PosY);    
  Mine(X + 1, Y + 1, PosX, PosY);     
  Mine(X, Y + 1, PosX, PosY);     
  Mine(X - 1, Y + 1, PosX, PosY);
  Mine(X - 1, Y, PosX, PosY);
  Mine(X - 1, Y - 1, PosX, PosY);
  Mine(X, Y - 1, PosX, PosY);
  Mine(X + 1, Y - 1, PosX, PosY);  
  
  AddToSystemJournal('Finished this location');
end;

begin

  //RuneBooks := [$40050CAF, $40053D22, $4004E5A6];
  OreTypes := [$19B7, $19B8, $19B9, $19BA];
  MiningTypes := [$0E85, $0E86];
  //OreTypes := [$19B9];
  
  SetEventProc(evIncomingGump, '');
  
  while not Terminated do begin
  
    if Dead then begin
      Terminated := True;
      Continue;
    end;    
    
    if not Connected() then begin
      Connect();
      Wait(10000);
      Continue;
    end;
  
    MinePoint(2431, 903);
    MinePoint(2434, 903);
    MinePoint(2437, 903);
    MinePoint(2440, 903);
    MinePoint(2443, 903);
    MinePoint(2446, 903);
    MinePoint(2441, 907);
    MinePoint(2439, 900);
    MinePoint(2440, 896);
    MinePoint(2443, 896);
    MinePoint(2446, 896);
    MinePoint(2448, 892);
    MinePoint(2448, 886);
    MinePoint(2448, 882);
    MinePoint(2445, 882);
    MinePoint(2442, 883);
    MinePoint(2438, 883);
    MinePoint(2435, 881);
    MinePoint(2438, 878);
    MinePoint(2441, 877);
    MinePoint(2445, 878);
    MinePoint(2436, 875);
    MinePoint(2435, 872);
    MinePoint(2432, 877);
    MinePoint(2443, 885);
    MinePoint(2443, 892);
    MinePoint(2449, 894);
    MinePoint(2448, 899);
    MinePoint(2447, 903);
    MinePoint(2443, 906);
  end;
end.
