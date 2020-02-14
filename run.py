import sys
import time

import config
import suikang
from logutil import logger


def let_us_start():
    # 假设调用接口花费 1s 的时间，从 20:00:00 开始调用预下单接口 60 次将花费 2min 的时间(请求本身1s、sleep1s)
    # 2min 之后已经没必要继续预约了，基本不会有了
    confirm_order_retry_max = 120  # 预约失败自动重试最大次数

    while True:
        # 直接调用 preorder 确认下单，没开始会返回错误: 预约未开始
        now = time.strftime("%H%M%S")
        if now < '195900':
            suikang.check_status()  # 不要持续使用 check_status() 接口，这个接口到 19:59:55 的时候可能就没响应了
            # logger.info('预约还没开始，请耐心等待~')
            time.sleep(60)
        elif '200000' <= now < '200500':
            retried = 0
            while True:
                success = suikang.comfire_order(config.MASK_TYPE)
                if success:
                    return
                elif retried <= confirm_order_retry_max:
                    retried += 1
                    time.sleep(1)
        elif now > '200500':
            logger.info('今天应该大概可能已经没有希望了，明天再来吧')
            exit(0)
        else:
            print('马上就要开始了，做好准备')
            time.sleep(1)


def read_command_args():
    args = sys.argv
    args_count = len(args) - 1
    if args_count == 1 and (args[1] == '-h' or args[1] == '--help'):
        print()
        print('    -n, --name          设置姓名')
        print('    -i, --id            设置身份证号码')
        print('    -m, --mobile        设置手机号码')
        print('    -t, --type          设置口罩类型, 1=N95(5个), 2=普通防护(10个)')
        print('    -s, --session       设置会话id')
        print('    --status-timeout    检查状态超时时间，单位：秒，默认 3 秒')
        print('    --order_timeout     下单接口超时时间，单位：秒，默认 2 秒')
        print()
        print('    -h, --help          查看所有参数', end='\n\n')
        exit(0)
    if args_count & 1 == 1:
        logger.error('[Check your arguments]检查输入参数')
        exit(1)
    for i in range(0, args_count >> 1):
        idx = i * 2
        key = args[idx + 1]
        val = args[idx + 2]
        logger.debug('{}={}'.format(key, str(val)))
        if key == '-n' or key == '--name':
            config.YOUR_NAME = str(val)
        elif key == '-i' or key == '--id':
            config.YOUR_IDNO = str(val)
        elif key == '-m' or key == '--mobile':
            config.YOUR_MOBILE = str(val)
        elif key == '-t' or key == '--type':
            config.MASK_TYPE = int(val)
        elif key == '-s' or key == '--session':
            config.LOGIN_SESSION_ID = str(val)
        elif key == '--status-timeout':
            config.CEHCK_STATUS_TIMEOUT_SECONDS = int(val)
        elif key == '--order_timeout':
            config.ORDER_TIMEOUT_SECONDS = int(val)
        else:
            logger.info('[Unknown Arguments]未知参数:{}={}'.format(key, str(val)))


if __name__ == "__main__":
    try:
        read_command_args()
        print('预约人:    %s' % config.YOUR_NAME)
        print('手机号:    %s' % config.YOUR_MOBILE)
        print('身份证:    %s' % config.YOUR_IDNO)
        print('口罩类型:  %s' % ('普通N95口罩' if config.MASK_TYPE == 1 else '普通防护口罩'))
        print('登陆会话:  %s' % config.LOGIN_SESSION_ID)
        print('开放预购:  20:00:00, 程序将在 19:59:30 开始尝试下单')
        let_us_start()
    except KeyboardInterrupt:
        print('Ctrl^C → 退出程序')
