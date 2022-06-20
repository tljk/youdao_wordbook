from main import Wordbook
import uasyncio

def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        # sys.exit()
    loop = uasyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def main():
    set_global_exception()  # Debug aid
    wb = Wordbook()
    await wb.lock.acquire()
    await uasyncio.gather(wb.crawler(),wb.button(),return_exceptions=True)

    wb.epd.sleep()
    wb.epd.font_free()
    wb.db.close()
    wb.wifi.active(False) 
    
try:
    uasyncio.run(main())
finally:
    uasyncio.new_event_loop()  # Clear retained state