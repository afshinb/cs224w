#!/usr/local/bin/python
#Generate date+value+Hash(PK) of txs
import binascii
from time import gmtime,strftime


DEST_FILE="p2pkh60180.csv"

def readVarInt(fileHead,c):
    txCount=fileHead.read(1)
    firstByte=int (  binascii.hexlify(txCount), 16 )
    
    if firstByte == 0xfd:       #Read 2 bytes
        x=fileHead.read(2)
        txCount= binascii.hexlify(x[::-1])
        c[0]+=3
    
    elif firstByte == 0xfe:     #Read 4 Bytes
        x = fileHead.read(4)
        txCount = binascii.hexlify(x[::-1])
        c[0]+=5
    
    elif firstByte == 0xff:     #Read 8 Bytes
        x = fileHead.read(8)
        txCount = binascii.hexlify(x[::-1])
        c[0]+=9
   
    else:
        #print "1byte!!!"
        txCount=binascii.hexlify(txCount)
        c[0]+=1

    return txCount          #Returns Hexlify string

def ReadInput(f,c):
    incounter=readVarInt(f,c)
    incounter=int(incounter,16)
    for i in range(incounter):
        chunk=f.read(32)
        c[0]+=32
        prevTXHASH= binascii.hexlify(chunk)

        chunk=f.read(4)
        c[0]+=4
        prevTXindex=binascii.hexlify(chunk)

        script_length = readVarInt(f,c)

        chunk=f.read( int(script_length,16) )
        c[0]+=int(script_length,16)
        txscript=binascii.hexlify(chunk)

        chunk=f.read(4)
        c[0]+=4
        sequence_number=binascii.hexlify(chunk)
    return

def ReadOutput(f,c,date):
    #Output Format: 8Bytes-> value, 1-9Bytes->Script length, as many bytes script
    #Script Format

    AddressList=[]
    outcounter=readVarInt(f,c)
    outcounter=int(outcounter,16)

    for i in range(outcounter):
        chunk=f.read(8)
        c[0]+=8
        value=binascii.hexlify(chunk[::-1])
        value= int(value,16)/10.0**8

        script_length = readVarInt(f,c)

        chunk=f.read (int (script_length,16) )
        c[0]+=(int (script_length,16) )
        outscript=binascii.hexlify(chunk)
        Address=ripAddress(outscript)
        AddressList.append( Address )

    #print AddressList
    return AddressList

def ripAddress(Outscript):
    #only rips p2pkh
    if Outscript[0:6]!= "76a914":       #OP_DUP - OP_HASH160 - bytes to push
        return 0
    else:
        Address=Outscript[6:]
    N=len(Address)
    if Address[N-4:] !="88ac":          #Last part of instruction for P2PKH
        return 0
    Address=Address[:N-4]
    return Address


#######################################

#######################
######  Block Header struct
    # #First four bytes are the magic number
    # Magic_Number=L[0:4]
    # #4 Bytes Block size
    # BlockSize=L[4:8]

    # #80 bytes block header
    # BlockHeader=L[8:88]

    # #Variable length integer 1-9 byets
    # #Little Endian
    #Blockheader info


def Read1BlockChain(f):

    #Magic Number should be 0xD9B4BEF9
    chunk = f.read(4)

    if chunk =="":
        print "EOF reached"
        return -1

    Magic_Number=chunk[::-1]
    Magic_Number=int(binascii.hexlify(Magic_Number),16)
    if Magic_Number != 0xD9B4BEF9:
        print "Warning! Mismatch in Magic Number",Magic_Number
    
    chunk=f.read(4)
    BlockSize=chunk[::-1]
    Size=int (binascii.hexlify( BlockSize),16)


    chunk=f.read(80)
    BlockHeader=chunk

    Version=BlockHeader[0:4][::-1]
    hashprevBlock=BlockHeader[4:36]
    hashMR=BlockHeader[36:36+32]
    time=BlockHeader[68:72][::-1]
    Bits=BlockHeader[72:76][::-1]
    Nonce=BlockHeader[76:80]

    t=int( binascii.hexlify(time) ,16)
    time_tx=strftime("%a, %d %b %Y %H:%M", gmtime(t) )
    c=[80]
    txCount = readVarInt(f,c)
    
    Block_tx=[]

    while (chunk != "" and c[0]<Size):
        chunk=f.read(4)     #Version
        version=binascii.hexlify(chunk[::-1])
        c[0]+=4

        if int(version,16) != 1:
            #print "Doomed!!!"
            print "Version is:" , int(version,16)
            #break

        #### Read input  # Currently returns nothing
        ReadInput(f,c)
        #########Output
        transactions=ReadOutput(f,c,time_tx)
        Block_tx+=transactions



        chunk=f.read(4)         #Lock time
        c[0]+=4
        lock_time=binascii.hexlify(chunk)

    writeToFile(Block_tx)
    return f        


def writeToFile(Block_tx):
    with open(DEST_FILE,"a" ) as f2:
        for item in Block_tx:
            f2.write(str (item)[1:-1]+"\n") 
    return


def ReadBlockFile(FILE_ADDRESS):
    with open(FILE_ADDRESS, "rb") as file_header:
        while file_header!= -1:
            file_header=Read1BlockChain(file_header)
    return


with open(DEST_FILE,"w") as f:
    f.write("PK_Hash\n")

for r in range (60,180):
    blknumber = str(r).zfill(5)
    FILE_ADDRESS="blk"+blknumber+".dat"
    ReadBlockFile(FILE_ADDRESS)
    print "Processed block:",blknumber

