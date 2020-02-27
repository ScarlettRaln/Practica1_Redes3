# coding=utf-8
import os
import sys
import time
import threading
import rrdtool
from os import remove
from os import path
from getSNMP import consultaSNMP
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from getSNMP_2 import consultaSNMP2


def worker(num, comunidad, host):
    """thread worker function"""
    namedb1 = "Multicast_recibidos_" + str(num)
    namedb2 = "IP_recibidos_" + str(num)
    namedb3 = "ICMP_enviados_" + str(num)
    namedb4 = "TCP_enviados_" + str(num)
    namedb5 = "UDP_recibidos_" + str(num)

    total_multicast = 0
    total_IP = 0
    total_ICMP = 0
    total_TCP = 0
    total_UDP = 0

    # SE CREAN LAS BASES DE DATOS

    ret = rrdtool.create(str(namedb1 + ".rrd"), "--start", 'N', "--step", '60', "DS:Multicast:COUNTER:600:U:U",
                         "RRA:AVERAGE:0.5:6:700")
    if ret:
        print(rrdtool.error())

    ret = rrdtool.create(str(namedb2 + ".rrd"), "--start", 'N', "--step", '60', "DS:recibidosIP:COUNTER:600:U:U",
                         "RRA:AVERAGE:0.5:6:700")
    if ret:
        print(rrdtool.error())

    ret = rrdtool.create(str(namedb3 + ".rrd"), "--start", 'N', "--step", '60', "DS:enviadosICMP:COUNTER:600:U:U",
                         "RRA:AVERAGE:0.5:6:700")
    if ret:
        print(rrdtool.error())

    ret = rrdtool.create(str(namedb4 + ".rrd"), "--start", 'N', "--step", '60', "DS:enviadosTCP:COUNTER:600:U:U",
                         "RRA:AVERAGE:0.5:6:700")
    if ret:
        print(rrdtool.error())

    ret = rrdtool.create(str(namedb5 + ".rrd"), "--start", 'N', "--step", '60', "DS:enviadosUDP:COUNTER:600:U:U",
                         "RRA:AVERAGE:0.5:6:700")
    if ret:
        print(rrdtool.error())

    # WHILE INFINITO PARA SOLICITAR INFORMACIÓN Y ACTUALIZAR
    while 1:
        total_multicast = int(consultaSNMP(comunidad, host, '1.3.6.1.2.1.2.2.1.12.2'))  # Depende de la interfaz D:
        valor = "N:" + str(total_multicast)
        # print (valor)
        rrdtool.update(str(namedb1 + ".rrd"), valor)
        rrdtool.dump(str(namedb1 + ".rrd"), str(namedb1 + ".xml"))

        total_IP = int(consultaSNMP(comunidad, host, '1.3.6.1.2.1.4.9.0'))
        valor = "N:" + str(total_IP)
        # print (valor)
        rrdtool.update(str(namedb2 + ".rrd"), valor)
        rrdtool.dump(str(namedb2 + ".rrd"), str(namedb2 + ".xml"))

        total_ICMP = int(consultaSNMP(comunidad, host, '1.3.6.1.2.1.5.22.0'))
        valor = "N:" + str(total_ICMP)
        # print (valor)
        rrdtool.update(str(namedb3 + ".rrd"), valor)
        rrdtool.dump(str(namedb3 + ".rrd"), str(namedb3 + ".xml"))

        total_TCP = int(consultaSNMP(comunidad, host, '1.3.6.1.2.1.6.11.0'))
        valor = "N:" + str(total_TCP)
        # print (valor)
        rrdtool.update(str(namedb4 + ".rrd"), valor)
        rrdtool.dump(str(namedb4 + ".rrd"), str(namedb4 + ".xml"))

        total_UDP = int(consultaSNMP(comunidad, host, '1.3.6.1.2.1.7.3.0'))
        valor = "N:" + str(total_UDP)
        # print (valor)
        rrdtool.update(str(namedb5 + ".rrd"), valor)
        rrdtool.dump(str(namedb5 + ".rrd"), str(namedb5 + ".xml"))

        time.sleep(1)

    if ret:
        print(rrdtool.error())
        time.sleep(300)

    # print('Worker: %s' % num)


num_agentes = 0
resp = 'Y'
while resp != 'N':

    estatus_monitoreo = 0
    k = 0
    j = 0
    l = 0
    listaleida = []
    lista_aux = []

    f = open("Datos.txt", 'r')
    for linea in f.readlines():
        value = linea.rstrip('\n')
        listaleida.append(value)
        lista_aux.append(value)
        j = j + 1
    f.close()

    numdisp = int(j / 4)

    print("**************************************************************")
    print("*                         Práctica 1                         *")
    print("*           Adquisición de información usando SNMP           *")
    print("*               González Ledesma Carla Daniela               *")
    print("**************************************************************\n")

    print("    1.- Inicio")
    print("    2.- Agregar Agente")
    print("    3.- Eliminar Agente")
    print("    4.- Generar Reporte\n")

    numero = int(input("Seleccione una opcion: "))

    if numero == 1:
        os.system("clear")
        print("\n****************************************************")
        print("*                    = Inicio =                    *")
        print("****************************************************\n")

        if numdisp != 0:
            print(" Dispositivos en monitoreo: ", numdisp)
            # Ahora ya sabiendo el numero de dispositivos que hay, obtendremos su informacion
            p = 0
            for k in range(numdisp):
                try:
                    name = str(consultaSNMP(listaleida[p + 2], listaleida[p], '1.3.6.1.2.1.1.1.0'))

                    if name == 'Hardware:':
                        name = "Windows"
                        _OID = '1.3.6.1.2.1.2.2.1.8.3'  # OID para la interfaz en el mio es el 3
                    else:  # Cuando name == Linux
                        _OID = '1.3.6.1.2.1.2.2.1.8.3'  # En caso de Linux como es nuestra compu es wlan0, hay que buscar que numero tiene

                    print("\n   >> Agente " + str(k + 1) + " : " + name)

                    OperStatus = consultaSNMP(listaleida[p + 2], listaleida[p], _OID)

                    if OperStatus == '1':
                        status = 'up'
                    elif OperStatus == '2':
                        status = 'down'
                    elif OperStatus == '3':
                        status = 'testing'

                    print("      Estatus del Monitoreo: ", status)

                    num_puertos = consultaSNMP(listaleida[p + 2], listaleida[p], '1.3.6.1.2.1.2.1.0')
                    print("      Numero de puertos disponibles: ", num_puertos)

                    for puertosh in range(int(num_puertos)):
                        num = puertosh + 1
                        _OID = "1.3.6.1.2.1.2.2.1.8." + str(num)
                        OperStatus = consultaSNMP(listaleida[p + 2], listaleida[p], _OID)

                        if OperStatus == '1':
                            status = 'up'
                        elif OperStatus == '2':
                            status = 'down'
                        elif OperStatus == '3':
                            status = 'testing'

                        print("        Puerto " + str(num) + " : " + status)
                except:
                    print("\n   >Agente " + str(k + 1) + "   Status: down")
                p = p + 4

        else:
            print("No hay Datos en el Registro! D:")
            time.sleep(1)

    elif numero == 2:
        os.system("clear")
        print("\n ****************************************")
        print(" *          = Agregar Agente =          *")
        print(" ****************************************\n")

        print(" Ingrese los siguientes datos\n")
        host = str(input("  > Host o direccion IP: "))
        version = int(input("  > Version SNMP: "))
        namecom = str(input("  > Nombre de la Comunidad: "))
        puerto = int(input("  > Puerto: "))

        lista = [host, version, namecom, puerto]

        f = open('Datos.txt', 'a')
        for i in lista:
            f.write(str(i))
            f.write("\n")
        f.close()

        num_agentes += 1

        threads = []
        t = threading.Thread(target=worker, args=(num_agentes, namecom, host))
        threads.append(t)
        t.start()

    elif numero == 3:
        os.system("clear")
        print("\n *****************************************")
        print(" *          = Eliminar Agente =          *")
        print(" *****************************************\n")

        print(" Agentes registrados: ")
        q = 0
        r = 0
        for i in range(numdisp):
            print("\n  >Agente ", i + 1)
            for r in range(4):
                print("    ", listaleida[q])
                q = q + 1

        print("\n Para regresar cancelar presione 0 ")
        delete_agente = int(input("\n Seleccione el numero de Agente que quiere eliminar: "))
        delete = (delete_agente - 1) * 4
        m = 0
        if delete_agente != 0:
            # Para eliminarlo del la lista leida del archivo de texto
            for m in range(4):
                listaleida.pop(delete)
            # reescribir el archivo con la información actual
            f = open('Datos.txt', 'w')
            for i in listaleida:
                f.write(str(i))
                f.write("\n")
            f.close()

            # Para detener el hilo

            # Para eliminar los archivos
            ndb1 = "Multicast_recibidos_" + str(delete_agente) + ".rrd"
            ndbxml1 = "Multicast_recibidos_" + str(delete_agente) + ".xml"
            ndb2 = "IP_recibidos_" + str(delete_agente) + ".rrd"
            ndbxml2 = "IP_recibidos_" + str(delete_agente) + ".xml"
            ndb3 = "ICMP_enviados_" + str(delete_agente) + ".rrd"
            ndbxml3 = "ICMP_enviados_" + str(delete_agente) + ".xml"
            ndb4 = "TCP_enviados_" + str(delete_agente) + ".rrd"
            ndbxml4 = "TCP_enviados_" + str(delete_agente) + ".xml"
            ndb5 = "UDP_recibidos_" + str(delete_agente) + ".rrd"
            ndbxml5 = "UDP_recibidos_" + str(delete_agente) + ".xml"

            if path.exists("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndb1):
                remove("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndb1)
            if path.exists("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndb2):
                remove("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndb2)
            if path.exists("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndb3):
                remove("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndb3)
            if path.exists("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndb4):
                remove("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndb4)
            if path.exists("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndb5):
                remove("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndb5)
            if path.exists("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndbxml1):
                remove("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndbxml1)
            if path.exists("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndbxml2):
                remove("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndbxml2)
            if path.exists("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndbxml3):
                remove("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndbxml3)
            if path.exists("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndbxml4):
                remove("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndbxml4)
            if path.exists("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndbxml5):
                remove("/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/" + ndbxml5)

            time.sleep(2)
            print("\n Agente eliminado Exitosamente! :D\n")

    elif numero == 4:
        os.system("clear")
        print("\n *****************************************")
        print(" *       = Generacion de Reporte =       *")
        print(" *****************************************\n")

        numAgente = int(input("Seleccione el Agente: "))
        p = (numAgente - 1) * 4

        tiempo_actual = int(time.time())
        tiempo_final = tiempo_actual - 60
        tiempo_inicial = tiempo_actual - 1800

        # Crear la imagen 1
        Img_Multicast = "/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/img/ImgMulticast_" + str(numAgente) + ".png"
        DEF_ = "DEF:entrada=Multicast_recibidos_"+ str(numAgente) + ".rrd:Multicast:AVERAGE"
        ret = rrdtool.graph(Img_Multicast, "--start", str(tiempo_inicial),"--end", "N","--vertical-label=Bytes/s",
                            "--title=Paquetes multicast",DEF_, "AREA:entrada#00FF00:In_Multicast")

        #Crear la imagen 2
        Img_IPv4 = "/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/img/ImgIPv4_" + str(numAgente) + ".png"
        DEF_ = "DEF:entrada=IP_recibidos_" + str(numAgente) + ".rrd:recibidosIP:AVERAGE"

        ret = rrdtool.graph(Img_IPv4,"--start", str(tiempo_inicial),"--end", "N","--vertical-label=Bytes/s",
                            "--title=Paquetes recibidos IPv4",DEF_,"AREA:entrada#00FF00:In IPv4")

        # Crear la imagen 3
        Img_IMCP = "/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/img/ImgIMCP_" + str(numAgente) + ".png"
        DEF_ = "DEF:entrada=ICMP_enviados_" + str(numAgente) + ".rrd:enviadosICMP:AVERAGE"

        ret = rrdtool.graph(Img_IMCP, "--start", str(tiempo_inicial), "--end", "N", "--vertical-label=Bytes/s",
                            "--title=Paquetes enviados ICMP", DEF_, "AREA:entrada#00FF00:Out ICMP")

        # Crear la imagen 4
        Img_TCP = "/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/img/Img_TCP_" + str(numAgente) + ".png"
        DEF_ = "DEF:entrada=TCP_enviados_" + str(numAgente) + ".rrd:enviadosTCP:AVERAGE"

        ret = rrdtool.graph(Img_TCP, "--start", str(tiempo_inicial), "--end", "N", "--vertical-label=Bytes/s",
                            "--title=Paquetes enviados TCP", DEF_, "AREA:entrada#00FF00:Out TCP")

        # Crear la imagen 5
        Img_UDP = "/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/img/Img_UDP_" + str(numAgente) + ".png"
        DEF_ = "DEF:entrada=UDP_recibidos_" + str(numAgente) + ".rrd:enviadosUDP:AVERAGE"

        ret = rrdtool.graph(Img_UDP, "--start", str(tiempo_inicial), "--end", "N", "--vertical-label=Bytes/s",
                            "--title=UDP's enviados", DEF_, "AREA:entrada#00FF00:Out UDP")

        name = str(consultaSNMP(listaleida[p + 2], listaleida[p], '1.3.6.1.2.1.1.1.0'))
        if name == 'Hardware:':
            urlImg = "/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/img/wn-logo.jpg"
        else:
            urlImg = "/home/scarlett/Escritorio/Redes_3/Practica1_Hilos/venv/img/ub-logo.png"

        nombre_Reporte = "Reporte del Agente " + str(numAgente) + ".pdf"

        doc = SimpleDocTemplate(nombre_Reporte, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=20, bottomMargin=18)

        Story = []
        logotipo = urlImg

        nombreAgente = str(consultaSNMP2(listaleida[p + 2], listaleida[p], '1.3.6.1.2.1.1.1.0'))
        numeroPuertos = str(consultaSNMP(listaleida[p + 2], listaleida[p], '1.3.6.1.2.1.2.1.0'))
        MILISEG = int(consultaSNMP(listaleida[p + 2], listaleida[p], '1.3.6.1.2.1.1.3.0')) / 1000
        SEG = MILISEG / 60
        ultimoReinicio = str(SEG)
        comunidad = listaleida[p + 2]
        ip = listaleida[p]

        imagen = Image(logotipo, 1 * inch, 1 * inch)
        Story.append(imagen)

        Story.append(Spacer(1, 8))

        estilos = getSampleStyleSheet()
        estilos.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

        name = nombreAgente.split()
        Agente = " "
        q = 0
        for desde in name:
            if (q > 1):
                Agente = Agente + " " + desde
            q = q + 1

        texto = ' %s' % Agente
        Story.append(Paragraph(texto, estilos["Justify"]))

        Story.append(Spacer(1, 2))

        texto = ">> Número de puertos: %s" % numeroPuertos
        Story.append(Paragraph(texto, estilos["Normal"]))

        Story.append(Spacer(1, 2))

        texto = ">> Tiempo de Actividad desde el último reinicio: %s" % ultimoReinicio + " minutos"
        Story.append(Paragraph(texto, estilos["Justify"]))

        Story.append(Spacer(1, 2))

        texto = ">> Comunidad: %s" % comunidad
        Story.append(Paragraph(texto, estilos["Normal"]))

        Story.append(Spacer(1, 2))

        texto = ">> Dirección IP: %s" % ip
        Story.append(Paragraph(texto, estilos["Normal"]))

        Story.append(Spacer(1, 12))

        # Imagen 1
        texto = 'Paquetes multicast que ha recibido una interfaz'
        Story.append(Paragraph(texto, estilos["Normal"]))
        Story.append(Spacer(1, 4))

        # Agrego la imagen 1 al Documento
        img = Image(Img_Multicast, 497 / 2, 173 / 2)
        Story.append(img)
        Story.append(Spacer(1, 8))

        # Imagen 2
        texto = 'Paquetes recibidos exitosamente, entregados a protocolos IPv4'
        Story.append(Paragraph(texto, estilos["Normal"]))
        Story.append(Spacer(1, 4))

        # Agrego la imagen 2 al Documento
        img = Image(Img_IPv4, 497 / 2, 173 / 2)
        Story.append(img)
        Story.append(Spacer(1, 8))

        # Imagen 3
        texto = 'Mensajes de respuesta ICMP que ha enviado el agente'
        Story.append(Paragraph(texto, estilos["Normal"]))
        Story.append(Spacer(1, 4))

        # Agrego la imagen 3 al Documento
        img = Image(Img_IMCP, 497 / 2, 173 / 2)
        Story.append(img)
        Story.append(Spacer(1, 8))

        # Imagen 4
        texto = 'Segmentos enviados, incluyendo los de las conexiones actuales pero excluyendo los que contienen solamente octetos retransmitidos'
        Story.append(Paragraph(texto, estilos["Normal"]))
        Story.append(Spacer(1, 4))

        # Agrego la imagen 4 al Documento
        img = Image(Img_TCP, 497 / 2, 173 / 2)
        Story.append(img)
        Story.append(Spacer(1, 8))

        # Imagen 5
        texto = 'Datagramas recibidos que no pudieron ser entregados por cuestiones distintas a la falta de aplicación en el puerto destino'
        Story.append(Paragraph(texto, estilos["Normal"]))
        Story.append(Spacer(1, 4))

        # Agrego la imagen 5 al Documento
        img = Image(Img_UDP, 497 / 2, 173 / 2)
        Story.append(img)
        Story.append(Spacer(1, 8))

        doc.build(Story)

        print("\n Su reporte ha sido generado exitosamente! :D ")

    resp = str(input("\n                   ¿Regresar al Menú?[Y/N] "))
    resp = resp.upper()
    os.system("clear")
