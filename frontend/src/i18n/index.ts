import { ref } from 'vue'

export type LocaleLang = 'vi' | 'en' | 'ko'

export const currentLocale = ref<LocaleLang>('vi')

export const messages: Record<LocaleLang, any> = {
  vi: {
    common: {
      appName: 'PRIMEVUE 4 AUTH',
      proBadge: 'PRO SHOWCASE',
      subtitle: 'Mẫu 1 Obsidian AI • Đa ngôn ngữ • OTP 6 số',
      themeLight: 'Sáng',
      themeDark: 'Tối',
      or: 'hoặc',
      backToLogin: 'Quay lại Đăng nhập',
      cancel: 'Hủy bỏ',
      confirm: 'Xác nhận',
      success: 'Thành công',
      error: 'Lỗi',
      loading: 'Đang xử lý...',
    },
    nav: {
      login: '1. Đăng nhập',
      register: '2. Đăng ký',
      forgot: '3. Quên mật khẩu',
      otp: '4. OTP (6 số)',
      logout: '5. Đăng xuất',
    },
    login: {
      title: 'Đăng nhập hệ thống',
      subtitle: 'Truy cập nền tảng AI Workspace bảo mật cao',
      orEmail: 'hoặc email',
      identifierLabel: 'Email hoặc Tên người dùng',
      identifierPlaceholder: 'developer@aipro.studio',
      passwordLabel: 'Mật khẩu',
      passwordPlaceholder: '••••••••',
      forgotPassword: 'Quên mật khẩu?',
      rememberMe: 'Ghi nhớ đăng nhập (30 ngày)',
      submitBtn: 'Đăng nhập ngay',
      noAccount: 'Chưa có tài khoản?',
      registerNow: 'Tạo tài khoản mới',
      errorEmpty: 'Vui lòng điền đầy đủ tài khoản và mật khẩu.',
      errorIdentifier: 'Vui lòng nhập Email hoặc Tên người dùng',
      errorPassword: 'Vui lòng nhập mật khẩu',
      successMsg: 'Đăng nhập thành công! Đang chuyển hướng sang bước xác thực OTP 6 số...',
      socialConnecting: 'Đang kết nối cổng OAuth bảo mật với {provider}...',
    },
    register: {
      title: 'Tạo tài khoản mới',
      subtitle: 'Điền thông tin và xác nhận mật khẩu để bắt đầu',
      usernameLabel: 'Tên người dùng (Username)',
      usernamePlaceholder: 'ví dụ: levietthang',
      emailLabel: 'Địa chỉ Email',
      emailPlaceholder: 'thang@aipro.studio',
      passwordLabel: 'Mật khẩu',
      passwordPlaceholder: 'Tối thiểu 8 ký tự',
      confirmPasswordLabel: 'Nhập lại mật khẩu',
      confirmPasswordPlaceholder: 'Nhập lại mật khẩu chính xác',
      submitBtn: 'Đăng ký tài khoản',
      hasAccount: 'Đã có tài khoản?',
      loginNow: 'Đăng nhập ngay',
      pwdPrompt: 'Nhập mật khẩu an toàn',
      pwdWeak: 'Yếu',
      pwdMedium: 'Trung bình',
      pwdStrong: 'Rất mạnh',
      pwdTipsTitle: 'Gợi ý mật khẩu an toàn:',
      pwdTip1: 'Ít nhất 8 ký tự',
      pwdTip2: 'Có chữ hoa, chữ số & ký tự đặc biệt',
      errorEmpty: 'Vui lòng kiểm tra và sửa các thông tin chưa chính xác bên dưới.',
      errorUsername: 'Tên người dùng tối thiểu 3 ký tự',
      errorUsernameEmpty: 'Vui lòng nhập tên người dùng',
      errorEmail: 'Địa chỉ email không đúng định dạng (ví dụ: user@example.com)',
      errorEmailEmpty: 'Vui lòng nhập địa chỉ email',
      errorPassword: 'Mật khẩu phải có ít nhất 8 ký tự',
      errorPasswordEmpty: 'Vui lòng thiết lập mật khẩu',
      errorConfirmPasswordEmpty: 'Vui lòng xác nhận lại mật khẩu',
      errorConfirmPasswordMismatch: 'Mật khẩu xác nhận không trùng khớp',
      successMsg: 'Đăng ký hoàn tất! Đang chuyển sang bước xác thực OTP 6 số...',
    },
    forgot: {
      title: 'Khôi phục mật khẩu',
      subtitle: 'Nhập email để nhận liên kết thiết lập lại mật khẩu',
      emailLabel: 'Email tài khoản',
      emailPlaceholder: 'name@aipro.studio',
      submitBtn: 'Gửi liên kết khôi phục',
      errorEmpty: 'Chưa điền thông tin email.',
      errorEmailEmpty: 'Vui lòng nhập địa chỉ email đã đăng ký',
      errorEmailInvalid: 'Địa chỉ email không đúng định dạng (ví dụ: name@company.com)',
      successTitle: 'Kiểm tra hộp thư của bạn',
      successSubtitle: 'Chúng tôi đã gửi hướng dẫn đặt lại mật khẩu tới {email}. Vui lòng kiểm tra hộp thư đến hoặc mục thư rác.',
      tryAnotherEmail: 'Thử lại với email khác',
    },
    otp: {
      title: 'Xác thực mã OTP 6 số',
      subtitle: 'Vui lòng nhập 6 chữ số bảo mật vừa được gửi tới {email}',
      quickDemoBtn: 'Dán nhanh mã thử nghiệm (729415)',
      submitBtn: 'Xác nhận mã bảo mật',
      notReceived: 'Không nhận được mã?',
      resendIn: 'Gửi lại sau ({countdown}s)',
      resendNow: 'Gửi lại mã ngay',
      errorIncomplete: 'Mã OTP chưa đủ 6 chữ số. Vui lòng nhập đầy đủ.',
      successMsg: 'Xác thực thành công với mã OTP [{code}]! Đang đăng nhập...',
      infoResent: 'Đã gửi lại mã OTP mới tới email của bạn (Mã thử nghiệm: 888999).',
      infoPasted: 'Đã tự động dán mã 6 số: 729415. Đang tự động kiểm tra...',
    },
    logout: {
      title: 'Đăng xuất tài khoản',
      subtitle: 'Xác nhận kết thúc phiên làm việc an toàn',
      confirmQuestion: 'Bạn có chắc chắn muốn đăng xuất khỏi hệ thống?',
      warningDesc: 'Các tab phiên làm việc hiện tại sẽ được lưu trữ và đóng bảo mật.',
      logoutAllDevices: 'Đăng xuất khỏi tất cả các thiết bị',
      logoutAllDevicesDesc: 'Hủy toàn bộ phiên đăng nhập trên điện thoại và trình duyệt khác',
      confirmBtn: 'Xác nhận Đăng xuất',
      cancelBtn: 'Ở lại phiên',
      successMsg: 'Đã đăng xuất thành công. Đang chuyển về trang Đăng nhập...',
    },
  },
  en: {
    common: {
      appName: 'PRIMEVUE 4 AUTH',
      proBadge: 'PRO SHOWCASE',
      subtitle: 'Obsidian AI Theme • Multi-language • 6-Digit OTP',
      themeLight: 'Light',
      themeDark: 'Dark',
      or: 'or',
      backToLogin: 'Back to Login',
      cancel: 'Cancel',
      confirm: 'Confirm',
      success: 'Success',
      error: 'Error',
      loading: 'Processing...',
    },
    nav: {
      login: '1. Sign In',
      register: '2. Register',
      forgot: '3. Forgot Password',
      otp: '4. OTP (6 Digits)',
      logout: '5. Sign Out',
    },
    login: {
      title: 'Sign In to Workspace',
      subtitle: 'Access your high-security AI Workspace platform',
      orEmail: 'or email',
      identifierLabel: 'Email or Username',
      identifierPlaceholder: 'developer@aipro.studio',
      passwordLabel: 'Password',
      passwordPlaceholder: '••••••••',
      forgotPassword: 'Forgot password?',
      rememberMe: 'Remember me for 30 days',
      submitBtn: 'Sign In',
      noAccount: "Don't have an account?",
      registerNow: 'Create an account',
      errorEmpty: 'Please enter both your account identifier and password.',
      errorIdentifier: 'Please enter your Email or Username',
      errorPassword: 'Please enter your password',
      successMsg: 'Signed in successfully! Redirecting to 6-digit OTP verification...',
      socialConnecting: 'Connecting secure OAuth handshake with {provider}...',
    },
    register: {
      title: 'Create Your Account',
      subtitle: 'Fill in your details and confirm password to get started',
      usernameLabel: 'Username',
      usernamePlaceholder: 'e.g. alex_dev',
      emailLabel: 'Email Address',
      emailPlaceholder: 'alex@aipro.studio',
      passwordLabel: 'Password',
      passwordPlaceholder: 'At least 8 characters',
      confirmPasswordLabel: 'Confirm Password',
      confirmPasswordPlaceholder: 'Re-enter your password accurately',
      submitBtn: 'Create Account',
      hasAccount: 'Already have an account?',
      loginNow: 'Sign In',
      pwdPrompt: 'Enter a strong password',
      pwdWeak: 'Weak',
      pwdMedium: 'Medium',
      pwdStrong: 'Strong',
      pwdTipsTitle: 'Password requirements:',
      pwdTip1: 'At least 8 characters long',
      pwdTip2: 'Includes uppercase, numbers & special characters',
      errorEmpty: 'Please correct the invalid fields highlighted below.',
      errorUsername: 'Username must be at least 3 characters',
      errorUsernameEmpty: 'Please enter a username',
      errorEmail: 'Please enter a valid email address (e.g. user@example.com)',
      errorEmailEmpty: 'Please enter your email address',
      errorPassword: 'Password must be at least 8 characters',
      errorPasswordEmpty: 'Please enter a password',
      errorConfirmPasswordEmpty: 'Please confirm your password',
      errorConfirmPasswordMismatch: 'Passwords do not match',
      successMsg: 'Registration complete! Redirecting to 6-digit OTP verification...',
    },
    forgot: {
      title: 'Reset Password',
      subtitle: 'Enter your email to receive password reset instructions',
      emailLabel: 'Account Email',
      emailPlaceholder: 'name@aipro.studio',
      submitBtn: 'Send Reset Link',
      errorEmpty: 'Email field cannot be empty.',
      errorEmailEmpty: 'Please enter your registered email address',
      errorEmailInvalid: 'Please enter a valid email address (e.g. name@company.com)',
      successTitle: 'Check Your Inbox',
      successSubtitle: 'We have sent password reset instructions to {email}. Please check your inbox or spam folder.',
      tryAnotherEmail: 'Try another email',
    },
    otp: {
      title: '6-Digit OTP Verification',
      subtitle: 'Please enter the 6-digit security code sent to {email}',
      quickDemoBtn: 'Paste demo code (729415)',
      submitBtn: 'Verify Code',
      notReceived: "Didn't receive the code?",
      resendIn: 'Resend in ({countdown}s)',
      resendNow: 'Resend code now',
      errorIncomplete: 'The OTP code must be 6 digits. Please fill completely.',
      successMsg: 'Verification successful with code [{code}]! Logging in...',
      infoResent: 'A new OTP code has been dispatched to your email (Demo: 888999).',
      infoPasted: 'Auto-pasted 6-digit code: 729415. Verifying automatically...',
    },
    logout: {
      title: 'Sign Out Account',
      subtitle: 'Confirm ending your secure workspace session',
      confirmQuestion: 'Are you sure you want to sign out of the system?',
      warningDesc: 'Your current session data will be saved securely before exiting.',
      logoutAllDevices: 'Sign out of all devices',
      logoutAllDevicesDesc: 'Revoke sessions on all other browsers and mobile devices',
      confirmBtn: 'Confirm Sign Out',
      cancelBtn: 'Stay Signed In',
      successMsg: 'Signed out safely. Redirecting to login page...',
    },
  },
  ko: {
    common: {
      appName: 'PRIMEVUE 4 AUTH',
      proBadge: 'PRO SHOWCASE',
      subtitle: '옵시디언 AI 테마 • 다국어 지원 • 6자리 OTP',
      themeLight: '라이트',
      themeDark: '다크',
      or: '또는',
      backToLogin: '로그인으로 돌아가기',
      cancel: '취소',
      confirm: '확인',
      success: '성공',
      error: '오류',
      loading: '처리 중...',
    },
    nav: {
      login: '1. 로그인',
      register: '2. 회원가입',
      forgot: '3. 비밀번호 찾기',
      otp: '4. OTP (6자리)',
      logout: '5. 로그아웃',
    },
    login: {
      title: '시스템 로그인',
      subtitle: '고보안 AI 워크스페이스 플랫폼에 접속하세요',
      orEmail: '또는 이메일',
      identifierLabel: '이메일 또는 사용자 이름',
      identifierPlaceholder: 'developer@aipro.studio',
      passwordLabel: '비밀번호',
      passwordPlaceholder: '••••••••',
      forgotPassword: '비밀번호를 잊으셨나요?',
      rememberMe: '로그인 상태 유지 (30일)',
      submitBtn: '로그인',
      noAccount: '계정이 없으신가요?',
      registerNow: '새 계정 만들기',
      errorEmpty: '아이디와 비밀번호를 모두 입력해 주세요.',
      errorIdentifier: '이메일 또는 사용자 이름을 입력하세요',
      errorPassword: '비밀번호를 입력하세요',
      successMsg: '로그인 성공! 6자리 OTP 인증 화면으로 이동합니다...',
      socialConnecting: '{provider} 보안 OAuth 연동 중...',
    },
    register: {
      title: '새 계정 만들기',
      subtitle: '정보를 입력하고 비밀번호를 확인하여 시작하세요',
      usernameLabel: '사용자 이름 (Username)',
      usernamePlaceholder: '예: alex_dev',
      emailLabel: '이메일 주소',
      emailPlaceholder: 'alex@aipro.studio',
      passwordLabel: '비밀번호',
      passwordPlaceholder: '최소 8자 이상',
      confirmPasswordLabel: '비밀번호 확인',
      confirmPasswordPlaceholder: '비밀번호를 다시 한 번 입력하세요',
      submitBtn: '회원가입 완료',
      hasAccount: '이미 계정이 있으신가요?',
      loginNow: '로그인하기',
      pwdPrompt: '안전한 비밀번호를 입력하세요',
      pwdWeak: '취약',
      pwdMedium: '보통',
      pwdStrong: '매우 강력',
      pwdTipsTitle: '비밀번호 안전 권장사항:',
      pwdTip1: '최소 8자 이상',
      pwdTip2: '대문자, 숫자 및 특수문자 포함',
      errorEmpty: '아래 표시된 잘못된 항목을 확인하고 수정해 주세요.',
      errorUsername: '사용자 이름은 최소 3자 이상이어야 합니다',
      errorUsernameEmpty: '사용자 이름을 입력하세요',
      errorEmail: '올바른 이메일 형식을 입력하세요 (예: user@example.com)',
      errorEmailEmpty: '이메일 주소를 입력하세요',
      errorPassword: '비밀번호는 최소 8자 이상이어야 합니다',
      errorPasswordEmpty: '비밀번호를 설정해 주세요',
      errorConfirmPasswordEmpty: '비밀번호 확인을 입력해 주세요',
      errorConfirmPasswordMismatch: '비밀번호가 일치하지 않습니다',
      successMsg: '회원가입 완료! 6자리 OTP 인증 단계로 이동합니다...',
    },
    forgot: {
      title: '비밀번호 재설정',
      subtitle: '가입하신 이메일로 비밀번호 재설정 링크를 보내드립니다',
      emailLabel: '계정 이메일',
      emailPlaceholder: 'name@aipro.studio',
      submitBtn: '재설정 링크 전송',
      errorEmpty: '이메일 주소를 입력해 주세요.',
      errorEmailEmpty: '등록된 이메일 주소를 입력하세요',
      errorEmailInvalid: '올바른 이메일 형식이 아닙니다 (예: name@company.com)',
      successTitle: '이메일 편지함을 확인하세요',
      successSubtitle: '{email} 주소로 비밀번호 재설정 안내를 전송했습니다. 수신함이나 스팸함을 확인해 주세요.',
      tryAnotherEmail: '다른 이메일로 시도하기',
    },
    otp: {
      title: '6자리 OTP 인증',
      subtitle: '{email}로 발송된 6자리 보안 코드를 입력해 주세요',
      quickDemoBtn: '테스트 코드 붙여넣기 (729415)',
      submitBtn: '보안 코드 인증',
      notReceived: '인증 코드를 받지 못하셨나요?',
      resendIn: '재전송 가능 ({countdown}초)',
      resendNow: '인증 코드 재전송',
      errorIncomplete: 'OTP 코드는 6자리 숫자여야 합니다. 모두 입력해 주세요.',
      successMsg: 'OTP 코드 [{code}] 인증 성공! 로그인 중...',
      infoResent: '새 OTP 코드가 이메일로 발송되었습니다 (테스트 코드: 888999).',
      infoPasted: '6자리 코드 729415 자동 입력 완료. 즉시 검증합니다...',
    },
    logout: {
      title: '계정 로그아웃',
      subtitle: '보안 워크스페이스 세션을 종료합니다',
      confirmQuestion: '시스템에서 로그아웃하시겠습니까?',
      warningDesc: '현재 작업 중인 세션 데이터가 안전하게 저장된 후 닫힙니다.',
      logoutAllDevices: '모든 기기에서 로그아웃',
      logoutAllDevicesDesc: '다른 모든 브라우저 및 모바일 기기의 세션을 즉시 만료합니다',
      confirmBtn: '로그아웃 확인',
      cancelBtn: '세션 유지',
      successMsg: '안전하게 로그아웃되었습니다. 로그인 화면으로 이동합니다...',
    },
  },
}

export function useI18n() {
  const locale = currentLocale

  function t(path: string, params?: Record<string, string | number>): string {
    const keys = path.split('.')
    let current: any = messages[locale.value]
    for (const k of keys) {
      if (current && typeof current === 'object' && k in current) {
        current = current[k]
      } else {
        // Fallback to English
        let fallback: any = messages['en']
        for (const fk of keys) {
          if (fallback && typeof fallback === 'object' && fk in fallback) {
            fallback = fallback[fk]
          } else {
            return path
          }
        }
        current = fallback
        break
      }
    }

    if (typeof current !== 'string') return path

    if (params) {
      let res = current
      for (const [pKey, pVal] of Object.entries(params)) {
        res = res.replace(new RegExp(`{${pKey}}`, 'g'), String(pVal))
      }
      return res
    }

    return current
  }

  function setLocale(newLocale: LocaleLang) {
    locale.value = newLocale
  }

  return {
    t,
    locale,
    setLocale,
  }
}
