class Format:
    @staticmethod
    def format_datetime(fecha):
        """
        Formatea una fecha y hora a un string legible.
        """
        return fecha.strftime('%d-%m-%Y %H:%M:%S') if fecha else "Fecha no disponible"
    
    @staticmethod
    def format_date(fecha):
        """
        Formatea una fecha a un string legible.
        Acepta datetime objects o strings en formato 'YYYY-MM-DD HH:MM:SS' o 'YYYY-MM-DD'.
        """
        if not fecha:
            return None
        
        # Si es string, convertir a datetime
        if isinstance(fecha, str):
            try:
                # Intentar formato con hora: '2025-07-17 00:00:00'
                if ' ' in fecha:
                    from datetime import datetime
                    fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
                else:
                    # Intentar formato solo fecha: '2025-07-17'
                    from datetime import datetime
                    fecha = datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                return None

        # Formatear a string legible
        return fecha.strftime('%d-%m-%Y')

    @staticmethod
    def month_to_text(month):
        """
        Convierte un número de mes a su representación textual.
        """
        month = int(month)
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        return months[month - 1] if 1 <= month <= 12 else "N/A"

    @staticmethod
    def separate_date(fecha):
        """
        Descompone una fecha en día, mes y año.
        """
        if fecha:
            dia, mes, anio = fecha.split("-")
            return int(dia), int(mes), int(anio)
        return None, None, None

    @staticmethod
    def format_phone_number(numero, extension_pais="57"):
        """
        Formatea y valida un número de teléfono móvil para API de WhatsApp.
        Solo acepta números móviles ya que WhatsApp no funciona con números fijos.
        
        Args:
            numero (str): Número de teléfono móvil a formatear
            extension_pais (str): Código de país (por defecto "57" para Colombia)
            
        Returns:
            str: Número formateado listo para WhatsApp API o None si es inválido
            
        Ejemplos:
            "3123456789" -> "573123456789"
            "+57 312 345 6789" -> "573123456789"
            "whatsapp:+573123456789" -> "573123456789"
            "312-345-6789" -> "573123456789"
            "12345" -> None (muy corto)
            "7123456" -> None (número fijo, no válido para WhatsApp)
        """
        if not numero:
            return None
        
        # Convertir a string si no lo es
        numero = str(numero).strip()
        
        if not numero:
            return None
        
        # Remover prefijos de Twilio
        if numero.startswith("whatsapp:"):
            numero = numero.replace("whatsapp:", "")
        
        # Limpiar caracteres no numéricos excepto el + inicial
        numero_limpio = ""
        plus_procesado = False
        
        for char in numero:
            if char.isdigit():
                numero_limpio += char
            elif char == "+" and not plus_procesado:
                numero_limpio += char
                plus_procesado = True
            # Ignorar espacios, guiones, paréntesis, etc.
        
        if not numero_limpio:
            return None
        
        # Manejar números que empiezan con +
        if numero_limpio.startswith("+"):
            numero_limpio = numero_limpio[1:]  # Remover el +
            
            # Verificar si ya tiene extensión de país
            if numero_limpio.startswith(extension_pais):
                # Ya tiene la extensión correcta
                numero_final = numero_limpio
            else:
                # Verificar si tiene otra extensión de país común
                extensiones_comunes = ["1", "52", "54", "56", "58", "591", "593", "594", "595", "598"]
                tiene_otra_extension = False
                
                for ext in extensiones_comunes:
                    if numero_limpio.startswith(ext):
                        # Tiene otra extensión, mantenerla
                        numero_final = numero_limpio
                        tiene_otra_extension = True
                        break
                
                if not tiene_otra_extension:
                    # No tiene extensión reconocida, agregar la por defecto
                    numero_final = extension_pais + numero_limpio
        else:
            # No empieza con +, verificar si ya tiene extensión
            if numero_limpio.startswith(extension_pais):
                numero_final = numero_limpio
            else:
                numero_final = extension_pais + numero_limpio

        if not numero_final.isdigit():
            return None
        
        if len(numero_final) < 8 or len(numero_final) > 15:
            return None
        
        # Verificaciones específicas por país
        if extension_pais == "57":  # Colombia
            # El número sin extensión debe tener exactamente 10 dígitos para móviles
            numero_sin_extension = numero_final[2:]
            if len(numero_sin_extension) != 10:
                return None
            
            # Números móviles deben empezar con 3
            if not numero_sin_extension.startswith("3"):
                return None
        
        return numero_final

    @staticmethod
    def quitar_extension_telefono(numero, extension_pais="57"):
        """
        Quita la extensión de país de un número de teléfono ya formateado y validado.
        Método inverso de formatear_telefono().
        
        Args:
            numero (str): Número de teléfono con extensión (ej: "573123456789")
            extension_pais (str): Código de país a remover (por defecto "57")
            
        Returns:
            str: Número sin extensión de país o None si no es válido
            
        Ejemplos:
            "573123456789" -> "3123456789" (Colombia)
            "+573123456789" -> "3123456789"
            "whatsapp:+573123456789" -> "3123456789"
            "15551234567" -> "5551234567" (USA, extension="1")
            "523312345678" -> "3312345678" (México, extension="52")
        """
        if not numero:
            return None
        
        # Convertir a string y limpiar
        numero = str(numero).strip()
        
        if not numero:
            return None
        
        # Remover prefijos de Twilio/WhatsApp
        if numero.startswith("whatsapp:"):
            numero = numero.replace("whatsapp:", "")
        
        # Remover el + si existe
        if numero.startswith("+"):
            numero = numero[1:]
        
        # Verificar que el número sea solo dígitos
        if not numero.isdigit():
            return None
        
        # Verificar si el número empieza con la extensión especificada
        if numero.startswith(extension_pais):
            # Quitar la extensión
            numero_sin_extension = numero[len(extension_pais):]
            
            # Verificar que quede algo después de quitar la extensión
            if numero_sin_extension:
                return numero_sin_extension
        
        # Si no empieza con la extensión especificada, retornar el número tal como está
        # porque puede ser un número local válido sin extensión
        return numero

    @staticmethod
    def datetime_bogota(timestamp_str=None):
        """
        Convierte un timestamp a datetime con zona horaria de América/Bogotá.
        Si no se proporciona timestamp_str, usa la hora actual.
        
        Args:
            timestamp_str (str/int, optional): String como "2025-08-11T15:29:56.559404",
                                             timestamp Unix como 1755016999,
                                             o None para usar hora actual
            
        Returns:
            datetime object con zona horaria de América/Bogotá
            
        Ejemplos:
            fecha_bogota() -> datetime actual en Bogotá
            fecha_bogota("2025-08-11T15:29:56.559404") -> datetime parseado en Bogotá
            fecha_bogota(1755016999) -> datetime desde timestamp Unix en Bogotá
            fecha_bogota("1755016999") -> datetime desde timestamp Unix en Bogotá
        """
        from datetime import datetime
        from dateutil.tz import gettz
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        
        bogota_tz = gettz('America/Bogota')
        
        # Si no se proporciona timestamp, usar hora actual
        if timestamp_str is None:
            return datetime.now().astimezone(bogota_tz)
        
        try:
            # Si es un número (timestamp Unix)
            if isinstance(timestamp_str, (int, float)):
                dt = datetime.fromtimestamp(timestamp_str, tz=timezone.utc)
                return dt.astimezone(bogota_tz)
            
            # Si es string, verificar si es timestamp Unix
            if isinstance(timestamp_str, str) and timestamp_str.isdigit():
                timestamp_unix = int(timestamp_str)
                dt = datetime.fromtimestamp(timestamp_unix, tz=timezone.utc)
                return dt.astimezone(bogota_tz)
            
            # Si es string con formato ISO
            dt = parse_datetime(timestamp_str)
            if dt is None:
                # Intentar formato ISO si falla el parsing
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Si no tiene zona horaria, asumir UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            # Convertir a zona horaria de Bogotá
            return dt.astimezone(bogota_tz)
            
        except (ValueError, AttributeError, TypeError, OSError) as e:
            print(f"Error parsing timestamp '{timestamp_str}': {e}")
            # Fallback: hora actual de Bogotá
            return datetime.now().astimezone(bogota_tz)
        
    @staticmethod
    def format_number(numero, separador_miles="."):
        """
        Formatea un número (float o string) con separadores de miles y sin decimales.
        
        Args:
            numero (float/str/int): Número a formatear
            separador_miles (str): Separador de miles (por defecto "." para formato colombiano)
            
        Returns:
            str: Número formateado con separadores o "0" si es inválido
            
        Ejemplos:
            formatear_numero(1234567.89) -> "1.234.568"
            formatear_numero("1234567.5") -> "1.234.568"
            formatear_numero("1234567") -> "1.234.567"
            formatear_numero(0) -> "0"
            formatear_numero("") -> "0"
            formatear_numero(None) -> "0"
        """
        if numero is None or numero == "":
            return "0"
        
        try:
            # Convertir a float si es string
            if isinstance(numero, str):
                # Limpiar el string de posibles caracteres no numéricos excepto punto y coma
                numero_limpio = numero.replace(",", "").replace(" ", "")
                if not numero_limpio or numero_limpio == "-":
                    return "0"
                numero = float(numero_limpio)
            elif isinstance(numero, int):
                numero = float(numero)
            elif not isinstance(numero, float):
                return "0"
            
            # Redondear para eliminar decimales
            numero_entero = int(round(numero))
            
            # Formatear con separadores de miles
            if separador_miles == ".":
                # Formato colombiano: puntos para miles
                return f"{numero_entero:,}".replace(",", ".")
            else:
                # Formato estándar: comas para miles
                return f"{numero_entero:,}"
                
        except (ValueError, TypeError, OverflowError):
            return "0"


    @staticmethod
    def clean_filename(text):
        import unicodedata
        import re
        # Eliminar tildes y caracteres no ASCII
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        # Reemplazar espacios por guiones bajos
        text = text.replace(' ', '_')
        # Eliminar cualquier carácter que no sea alfanumérico, guion o guion bajo
        text = re.sub(r'[^A-Za-z0-9_\-]', '', text)
        # text = text.lower()
        return text
    
    @staticmethod
    def safe_isoformat(date_obj):
        """Convierte una fecha/datetime a string ISO de manera segura"""
        if date_obj is None:
            return None
        if isinstance(date_obj, str):
            return date_obj
        if hasattr(date_obj, 'isoformat'):
            return date_obj.isoformat()
        return str(date_obj)