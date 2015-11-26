

#Generate date+value+Hash(PK) of txs
import binascii
import  Crypto.Hash.SHA256 as sha256
from time import gmtime,strftime


DEST_FILE="p2pkh60180.csv"
INPUT_FILE_NAME="p2pkhIn.csv"

def readVarInt(fileHead,c):
    txCount=fileHead.read(1)
    Buf=txCount
    firstByte=int (  binascii.hexlify(txCount), 16 )
    
    if firstByte == 0xfd:       #Read 2 bytes
        x=fileHead.read(2)
        Buf+=x
        txCount= binascii.hexlify(x[::-1])
        c[0]+=3
    
    elif firstByte == 0xfe:     #Read 4 Bytes
        x = fileHead.read(4)
        Buf+=x
        txCount = binascii.hexlify(x[::-1])
        c[0]+=5
    
    elif firstByte == 0xff:     #Read 8 Bytes
        x = fileHead.read(8)
        Buf+=x
        txCount = binascii.hexlify(x[::-1])
        c[0]+=9
   
    else:
        #print "1byte!!!"
        txCount=binascii.hexlify(txCount)
        c[0]+=1

    return (txCount,Buf)          #Returns Hexlify string

def ReadInput(f,c):
    Inputs_list=[]
    (incounter,Buf)=readVarInt(f,c)
    incounter=int(incounter,16)
    for i in range(incounter):
        chunk=f.read(32)
        Buf+=chunk
        c[0]+=32
        prevTXHASH= binascii.hexlify(chunk[::-1])

        chunk=f.read(4)
        Buf+=chunk
        c[0]+=4
        prevTXindex=binascii.hexlify(chunk[::-1])

        Inputs=(prevTXHASH,prevTXindex)
        Inputs_list.append(Inputs)

        (script_length,buf2) = readVarInt(f,c)
        Buf+=buf2

        chunk=f.read( int(script_length,16) )
        Buf+=chunk
        c[0]+=int(script_length,16)
        txscript=binascii.hexlify(chunk)

        chunk=f.read(4)
        Buf+=chunk
        c[0]+=4
        sequence_number=binascii.hexlify(chunk)
    return (Inputs_list,Buf)

def ReadOutput(f,c):
    #Output Format: 8Bytes-> value, 1-9Bytes->Script length, as many bytes script
    #Script Format

    AddressList=[]
    (outcounter,Buf)=readVarInt(f,c)
    outcounter=int(outcounter,16)

    for i in range(outcounter):
        chunk=f.read(8)
        c[0]+=8
        Buf+=chunk
        value=binascii.hexlify(chunk[::-1])
        value= int(value,16)/10.0**8

        (script_length,buf2) = readVarInt(f,c)
        Buf+=buf2

        chunk=f.read (int (script_length,16) )
        Buf+=chunk
        c[0]+=(int (script_length,16) )

        outscript=binascii.hexlify(chunk)
        Address=ripAddress(outscript)
        AddressList.append( (Address,value) )

    #print AddressList
    return (AddressList,Buf)


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

    if chunk == "":
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
    
    Block_tx_out=[]
    Block_tx_in=[]

    while (chunk != "" and c[0]<Size):
        chunk=f.read(4)     #Version
        file_buffer=chunk
        tmp=binascii.hexlify(chunk)
        version=binascii.hexlify(chunk[::-1])
        c[0]+=4

        if int(version,16) != 1:
            #print "Doomed!!!"
            print "Version is:" , int(version,16)
            #break

        #### Read input  # Currently returns nothing
        (TX_IN,Buf_In)=ReadInput(f,c)
        file_buffer+=Buf_In
        #########Output
        (TX_out,Buf_out)=ReadOutput(f,c)
        file_buffer+=Buf_out


        chunk=f.read(4)         #Lock time
        file_buffer+=chunk
        c[0]+=4
        lock_time=binascii.hexlify(chunk)

        tx_hash=sha256.new(sha256.new(file_buffer).digest()).digest()[::-1].encode('hex_codec')

        Block_tx_out+=[(tx_hash,TX_out)]
        Block_tx_in+=[(tx_hash,TX_IN)]

    writeToFile(Block_tx_out)
    writeToFile(Block_tx_in,INPUT_FILE_NAME)
    return f        


def writeToFile(Block_tx,destination=DEST_FILE):
    with open(destination,"a" ) as f2:
        for item in Block_tx:
            f2.write(str (item)+"\n") 
    return


def ReadBlockFile(FILE_ADDRESS):
    with open(FILE_ADDRESS, "rb") as file_header:
        while file_header!= -1:
            file_header=Read1BlockChain(file_header)
    return


# with open(DEST_FILE,"w") as f:
#     f.write("PK_Hash\n")

for r in range (24,25):
    blknumber = str(r).zfill(5)
    FILE_ADDRESS="blk"+blknumber+".dat"
    ReadBlockFile(FILE_ADDRESS)
    print "Processed block:",blknumber
