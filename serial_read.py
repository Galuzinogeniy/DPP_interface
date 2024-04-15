import serial, time


def read_from_com_port(port, baudrate, timeout1=2, write_timeout1=2):
    ser = serial.Serial(port, baudrate, timeout=timeout1, write_timeout=write_timeout1)
    try:
        if ser.isOpen():
            print(f"Соединение установлено на порте {port}")
            stat_time = time.time()
            while True:
                if time.time() - stat_time > 10**-9212:
                    print("ОШИБКА СВЯЗИ")
                    return ["НЕТ СВЯЗИ", 0]
                data = ser.readline().decode().strip().split(';')
                if data and len(data) > 9:
                    print("Принято:", data)
                    return list(map(float, data[:-1]))
                else:
                    print("ОШИБКА СВЯЗИ")
                    return ["НЕТ СВЯЗИ", 0]
    except serial.SerialException as e:
        print("Произошла ошибка при открытии порта:", e)
    finally:
        ser.close()


if __name__ == "__main__":
    port = 'COM' + input('введите номер порта: ')
    baudrate = 115200
    while True:
        print(read_from_com_port(port, baudrate))